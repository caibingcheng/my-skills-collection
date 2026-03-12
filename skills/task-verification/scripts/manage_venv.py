#!/usr/bin/env python3
"""
虚拟环境管理工具 - 创建和管理验证用的隔离环境
"""

import sys
import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import Optional, Dict, List
import tempfile
import shutil


class VirtualEnvManager:
    """虚拟环境管理器"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(tempfile.mkdtemp(prefix='task-verify-'))
        self.venv_path = None
        self.errors = []

    def detect_available_tools(self) -> Dict[str, bool]:
        """检测可用的虚拟化工具"""
        tools = {}

        # 检查Python venv
        tools['python_venv'] = self._check_command(['python3', '-m', 'venv', '--help'])

        # 检查Docker
        tools['docker'] = self._check_command(['docker', '--version'])

        # 检查Podman
        tools['podman'] = self._check_command(['podman', '--version'])

        return tools

    def _check_command(self, cmd: List[str]) -> bool:
        """检查命令是否可用"""
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def create_python_venv(self, name: str = 'verify-env', requirements: Optional[str] = None) -> dict:
        """创建Python虚拟环境"""
        result = {
            'type': 'python_venv',
            'name': name,
            'path': None,
            'created': False,
            'errors': []
        }

        venv_path = self.base_path / name

        try:
            # 创建venv
            subprocess.run(['python3', '-m', 'venv', str(venv_path)], check=True, capture_output=True)
            result['created'] = True
            result['path'] = str(venv_path)
            self.venv_path = venv_path

            # 获取Python路径
            if os.name == 'nt':
                python_path = venv_path / 'Scripts' / 'python.exe'
            else:
                python_path = venv_path / 'bin' / 'python'
            result['python_path'] = str(python_path)

            # 安装requirements
            if requirements and Path(requirements).exists():
                pip_result = subprocess.run(
                    [str(python_path), '-m', 'pip', 'install', '-r', requirements],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                result['requirements_installed'] = pip_result.returncode == 0
                if not result['requirements_installed']:
                    result['errors'].append(f"Failed to install requirements: {pip_result.stderr[:500]}")

        except subprocess.CalledProcessError as e:
            result['errors'].append(f"Failed to create venv: {e}")
        except Exception as e:
            result['errors'].append(f"Error: {e}")

        self.errors.extend(result['errors'])
        return result

    def create_docker_container(self, image: str = 'python:3.11-slim', name: Optional[str] = None,
                                 mounts: Optional[List[str]] = None) -> dict:
        """创建Docker容器进行验证"""
        result = {
            'type': 'docker',
            'image': image,
            'container_id': None,
            'created': False,
            'errors': []
        }

        container_name = name or f"verify-{os.urandom(4).hex()}"

        try:
            # 构建docker run命令
            cmd = ['docker', 'run', '-d', '--name', container_name]

            # 添加挂载
            if mounts:
                for mount in mounts:
                    cmd.extend(['-v', mount])

            # 保持容器运行
            cmd.extend([image, 'sleep', '3600'])

            docker_result = subprocess.run(cmd, capture_output=True, text=True)

            if docker_result.returncode == 0:
                result['created'] = True
                result['container_id'] = docker_result.stdout.strip()
                result['container_name'] = container_name
            else:
                result['errors'].append(f"Docker run failed: {docker_result.stderr}")

        except Exception as e:
            result['errors'].append(f"Error: {e}")

        self.errors.extend(result['errors'])
        return result

    def create_podman_container(self, image: str = 'python:3.11-slim', name: Optional[str] = None,
                                 mounts: Optional[List[str]] = None) -> dict:
        """创建Podman容器进行验证"""
        result = {
            'type': 'podman',
            'image': image,
            'container_id': None,
            'created': False,
            'errors': []
        }

        container_name = name or f"verify-{os.urandom(4).hex()}"

        try:
            cmd = ['podman', 'run', '-d', '--name', container_name]

            if mounts:
                for mount in mounts:
                    cmd.extend(['-v', mount])

            cmd.extend([image, 'sleep', '3600'])

            podman_result = subprocess.run(cmd, capture_output=True, text=True)

            if podman_result.returncode == 0:
                result['created'] = True
                result['container_id'] = podman_result.stdout.strip()
                result['container_name'] = container_name
            else:
                result['errors'].append(f"Podman run failed: {podman_result.stderr}")

        except Exception as e:
            result['errors'].append(f"Error: {e}")

        self.errors.extend(result['errors'])
        return result

    def run_in_venv(self, command: List[str], cwd: Optional[str] = None) -> dict:
        """在虚拟环境中运行命令"""
        if not self.venv_path:
            return {'success': False, 'error': 'No venv created'}

        # 获取venv中的Python
        if os.name == 'nt':
            python_path = self.venv_path / 'Scripts' / 'python.exe'
        else:
            python_path = self.venv_path / 'bin' / 'python'

        # 如果命令是Python脚本，使用venv的Python
        if command[0].endswith('.py'):
            cmd = [str(python_path)] + command
        elif command[0] == 'python' or command[0] == 'python3':
            cmd = [str(python_path)] + command[1:]
        else:
            cmd = command

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run_in_container(self, container_id: str, command: List[str]) -> dict:
        """在容器中运行命令"""
        try:
            cmd = ['docker', 'exec', container_id] + command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def cleanup(self):
        """清理虚拟环境"""
        if self.venv_path and self.venv_path.exists():
            try:
                shutil.rmtree(self.venv_path)
            except Exception as e:
                self.errors.append(f"Failed to cleanup venv: {e}")


def main():
    parser = argparse.ArgumentParser(description='Manage virtual environments for verification')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # detect command
    detect_parser = subparsers.add_parser('detect', help='Detect available tools')

    # create command
    create_parser = subparsers.add_parser('create', help='Create virtual environment')
    create_parser.add_argument('--type', choices=['venv', 'docker', 'podman'], required=True)
    create_parser.add_argument('--name', default='verify-env', help='Environment name')
    create_parser.add_argument('--requirements', help='Requirements file for venv')
    create_parser.add_argument('--image', default='python:3.11-slim', help='Docker/Podman image')
    create_parser.add_argument('--base-path', help='Base path for environments')

    # run command
    run_parser = subparsers.add_parser('run', help='Run command in environment')
    run_parser.add_argument('--venv', help='Path to venv')
    run_parser.add_argument('--container', help='Container ID')
    run_parser.add_argument('cmd', nargs='+', help='Command to run')

    # cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup environment')
    cleanup_parser.add_argument('--path', required=True, help='Path to clean up')

    # Global options
    parser.add_argument('--json', action='store_true', help='Output in JSON format')

    args = parser.parse_args()

    manager = VirtualEnvManager(getattr(args, 'base_path', None))

    if args.command == 'detect':
        tools = manager.detect_available_tools()
        if args.json:
            print(json.dumps(tools, indent=2))
        else:
            print("Available tools:")
            for tool, available in tools.items():
                print(f"  {tool}: {'✓' if available else '✗'}")

    elif args.command == 'create':
        if args.type == 'venv':
            result = manager.create_python_venv(args.name, args.requirements)
        elif args.type == 'docker':
            result = manager.create_docker_container(args.image, args.name)
        elif args.type == 'podman':
            result = manager.create_podman_container(args.image, args.name)
        else:
            result = {'error': 'Unknown type'}

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Environment type: {result['type']}")
            print(f"Created: {result['created']}")
            if result.get('path'):
                print(f"Path: {result['path']}")
            if result.get('container_id'):
                print(f"Container ID: {result['container_id']}")
            if result.get('errors'):
                print("Errors:")
                for error in result['errors']:
                    print(f"  - {error}")

    elif args.command == 'run':
        if args.venv:
            manager.venv_path = Path(args.venv)
            result = manager.run_in_venv(args.cmd)
        elif args.container:
            result = manager.run_in_container(args.container, args.cmd)
        else:
            result = {'error': 'Must specify --venv or --container'}

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Success: {result['success']}")
            if result.get('stdout'):
                print(f"stdout: {result['stdout']}")
            if result.get('stderr'):
                print(f"stderr: {result['stderr']}")

    elif args.command == 'cleanup':
        manager.venv_path = Path(args.path)
        manager.cleanup()
        if manager.errors:
            print(f"Errors during cleanup: {manager.errors}")
        else:
            print("Cleanup completed")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
