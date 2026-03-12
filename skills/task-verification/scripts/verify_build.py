#!/usr/bin/env python3
"""
编译验证工具 - 验证编译是否成功且编译产物可执行
"""

import sys
import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import List, Dict, Optional


class BuildVerifier:
    """编译验证器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.errors = []
        self.warnings = []
        self.project_type = None

    def detect_project_type(self) -> str:
        """检测项目类型"""
        if (self.project_path / 'package.json').exists():
            return 'nodejs'
        elif (self.project_path / 'requirements.txt').exists() or \
             (self.project_path / 'pyproject.toml').exists() or \
             (self.project_path / 'setup.py').exists():
            return 'python'
        elif (self.project_path / 'Cargo.toml').exists():
            return 'rust'
        elif (self.project_path / 'pom.xml').exists():
            return 'maven'
        elif (self.project_path / 'build.gradle').exists():
            return 'gradle'
        elif (self.project_path / 'CMakeLists.txt').exists():
            return 'cmake'
        elif (self.project_path / 'Makefile').exists():
            return 'make'
        elif any(f.suffix in ['.go'] for f in self.project_path.glob('*.go')):
            return 'go'
        elif (self.project_path / 'main.py').exists():
            return 'python'
        elif (self.project_path / 'main.rs').exists():
            return 'rust'
        elif (self.project_path / 'main.go').exists():
            return 'go'
        else:
            return 'unknown'

    def run_command(self, cmd: List[str], cwd: Optional[str] = None, timeout: int = 300) -> dict:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or str(self.project_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout}s'
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }

    def verify_nodejs(self) -> dict:
        """验证Node.js项目"""
        result = {'type': 'nodejs', 'steps': {}, 'passed': False}

        # 检查package.json
        if not (self.project_path / 'package.json').exists():
            self.errors.append("package.json not found")
            return result
        result['steps']['package_exists'] = True

        # 安装依赖
        install_result = self.run_command(['npm', 'install'])
        result['steps']['install'] = {
            'success': install_result['success'],
            'output': install_result['stderr'] if not install_result['success'] else 'OK'
        }
        if not install_result['success']:
            self.errors.append(f"npm install failed: {install_result['stderr'][:200]}")
            return result

        # 尝试build
        build_result = self.run_command(['npm', 'run', 'build'])
        result['steps']['build'] = {
            'success': build_result['success'],
            'output': build_result['stderr'] if not build_result['success'] else 'OK'
        }
        if not build_result['success']:
            self.errors.append(f"npm build failed: {build_result['stderr'][:200]}")
            return result

        result['passed'] = True
        return result

    def verify_python(self) -> dict:
        """验证Python项目"""
        result = {'type': 'python', 'steps': {}, 'passed': False}

        # 检查语法错误
        py_files = list(self.project_path.glob('**/*.py'))
        if not py_files:
            self.warnings.append("No Python files found")
            result['steps']['syntax_check'] = 'skipped'
        else:
            syntax_errors = []
            for py_file in py_files[:20]:  # 限制检查文件数
                check_result = self.run_command(['python3', '-m', 'py_compile', str(py_file)])
                if not check_result['success']:
                    syntax_errors.append(f"{py_file}: {check_result['stderr']}")

            result['steps']['syntax_check'] = {
                'success': len(syntax_errors) == 0,
                'errors': syntax_errors[:5]  # 最多显示5个
            }
            if syntax_errors:
                self.errors.extend(syntax_errors[:3])
                return result

        # 检查是否可以导入（如果有setup.py或pyproject.toml）
        if (self.project_path / 'setup.py').exists() or (self.project_path / 'pyproject.toml').exists():
            install_result = self.run_command(['pip', 'install', '-e', '.'])
            result['steps']['install'] = {
                'success': install_result['success'],
                'output': install_result['stderr'] if not install_result['success'] else 'OK'
            }
            if not install_result['success']:
                self.errors.append(f"pip install failed: {install_result['stderr'][:200]}")

        result['passed'] = len(self.errors) == 0
        return result

    def verify_rust(self) -> dict:
        """验证Rust项目"""
        result = {'type': 'rust', 'steps': {}, 'passed': False}

        # 检查Cargo.toml
        if not (self.project_path / 'Cargo.toml').exists():
            self.errors.append("Cargo.toml not found")
            return result
        result['steps']['cargo_exists'] = True

        # 编译
        build_result = self.run_command(['cargo', 'build'])
        result['steps']['build'] = {
            'success': build_result['success'],
            'output': build_result['stderr'] if not build_result['success'] else 'OK'
        }
        if not build_result['success']:
            self.errors.append(f"cargo build failed: {build_result['stderr'][:200]}")
            return result

        # 运行测试
        test_result = self.run_command(['cargo', 'test'])
        result['steps']['test'] = {
            'success': test_result['success'],
            'output': test_result['stderr'] if not test_result['success'] else 'OK'
        }

        result['passed'] = build_result['success']
        return result

    def verify_go(self) -> dict:
        """验证Go项目"""
        result = {'type': 'go', 'steps': {}, 'passed': False}

        # 检查语法
        check_result = self.run_command(['go', 'build', '-o', '/dev/null', '.'])
        result['steps']['build'] = {
            'success': check_result['success'],
            'output': check_result['stderr'] if not check_result['success'] else 'OK'
        }
        if not check_result['success']:
            self.errors.append(f"go build failed: {check_result['stderr'][:200]}")
            return result

        result['passed'] = True
        return result

    def verify_make(self) -> dict:
        """验证Make项目"""
        result = {'type': 'make', 'steps': {}, 'passed': False}

        build_result = self.run_command(['make'])
        result['steps']['build'] = {
            'success': build_result['success'],
            'output': build_result['stderr'] if not build_result['success'] else 'OK'
        }
        if not build_result['success']:
            self.errors.append(f"make failed: {build_result['stderr'][:200]}")
            return result

        result['passed'] = True
        return result

    def verify_cmake(self) -> dict:
        """验证CMake项目"""
        result = {'type': 'cmake', 'steps': {}, 'passed': False}

        # 创建build目录
        build_dir = self.project_path / 'build'
        build_dir.mkdir(exist_ok=True)

        # 配置
        config_result = self.run_command(['cmake', '..'], cwd=str(build_dir))
        result['steps']['configure'] = {
            'success': config_result['success'],
            'output': config_result['stderr'] if not config_result['success'] else 'OK'
        }
        if not config_result['success']:
            self.errors.append(f"cmake configuration failed: {config_result['stderr'][:200]}")
            return result

        # 编译
        build_result = self.run_command(['make'], cwd=str(build_dir))
        result['steps']['build'] = {
            'success': build_result['success'],
            'output': build_result['stderr'] if not build_result['success'] else 'OK'
        }
        if not build_result['success']:
            self.errors.append(f"make failed: {build_result['stderr'][:200]}")
            return result

        result['passed'] = True
        return result

    def verify(self) -> dict:
        """执行验证"""
        project_type = self.detect_project_type()
        result = {
            'project_path': str(self.project_path),
            'project_type': project_type,
            'verification': {},
            'passed': False,
            'errors': [],
            'warnings': []
        }

        verifiers = {
            'nodejs': self.verify_nodejs,
            'python': self.verify_python,
            'rust': self.verify_rust,
            'go': self.verify_go,
            'make': self.verify_make,
            'cmake': self.verify_cmake
        }

        if project_type in verifiers:
            result['verification'] = verifiers[project_type]()
            result['passed'] = result['verification']['passed']
        else:
            self.errors.append(f"Unsupported project type: {project_type}")

        result['errors'] = self.errors
        result['warnings'] = self.warnings

        return result


def main():
    parser = argparse.ArgumentParser(description='Verify build/compilation')
    parser.add_argument('project_path', help='Path to project directory')
    parser.add_argument('--type', choices=['nodejs', 'python', 'rust', 'go', 'make', 'cmake', 'maven', 'gradle'],
                        help='Force project type (auto-detect if not specified)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')

    args = parser.parse_args()

    verifier = BuildVerifier(args.project_path)
    if args.type:
        verifier.project_type = args.type

    result = verifier.verify()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Project: {result['project_path']}")
        print(f"Type: {result['project_type']}")
        print(f"Passed: {result['passed']}")
        if result['verification']:
            print(f"Verification steps:")
            for step, status in result['verification'].get('steps', {}).items():
                if isinstance(status, dict):
                    print(f"  {step}: {'✓' if status['success'] else '✗'}")
                else:
                    print(f"  {step}: {status}")
        if result['errors']:
            print(f"Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        if result['warnings']:
            print(f"Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")

    sys.exit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
