#!/usr/bin/env python3
"""
脚本验证工具 - 验证脚本是否可执行且符合预期
"""

import sys
import subprocess
import argparse
import os
import tempfile
import json
from pathlib import Path
from typing import Optional, List


def check_file_exists(script_path: str) -> bool:
    """检查脚本文件是否存在"""
    return Path(script_path).exists()


def check_is_executable(script_path: str) -> bool:
    """检查脚本是否可执行"""
    return os.access(script_path, os.X_OK)


def check_shebang(script_path: str) -> bool:
    """检查脚本是否有shebang行"""
    try:
        with open(script_path, 'r') as f:
            first_line = f.readline()
            return first_line.startswith('#!')
    except Exception:
        return False


def run_script_safely(script_path: str, args: Optional[List[str]] = None, timeout: int = 30) -> dict:
    """
    安全地运行脚本并返回结果

    返回: {
        'success': bool,
        'returncode': int,
        'stdout': str,
        'stderr': str,
        'duration': float
    }
    """
    args = args or []
    cmd = [script_path] + args

    start_time = subprocess.run(['date', '+%s.%N'], capture_output=True, text=True).stdout.strip()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )

        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': result.returncode  # 简化处理
        }
    except subprocess.TimeoutExpired as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': f'Timeout after {timeout} seconds',
            'duration': timeout
        }
    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'duration': 0
        }


def verify_script(script_path: str, expected_output: Optional[str] = None, expected_returncode: int = 0, args: Optional[List[str]] = None) -> dict:
    """
    验证脚本是否可执行且符合预期

    Args:
        script_path: 脚本路径
        expected_output: 期望的输出内容（可选）
        expected_returncode: 期望的返回码（默认0）
        args: 传递给脚本的参数

    Returns:
        验证结果字典
    """
    result = {
        'script': script_path,
        'passed': False,
        'checks': {},
        'errors': []
    }

    # 检查文件存在
    if not check_file_exists(script_path):
        result['errors'].append(f"Script not found: {script_path}")
        return result
    result['checks']['exists'] = True

    # 检查可执行权限
    if not check_is_executable(script_path):
        # 尝试添加可执行权限
        try:
            os.chmod(script_path, os.stat(script_path).st_mode | 0o111)
            result['checks']['executable'] = True
            result['checks']['chmod_applied'] = True
        except Exception as e:
            result['checks']['executable'] = False
            result['errors'].append(f"Script not executable and chmod failed: {e}")
    else:
        result['checks']['executable'] = True

    # 检查shebang（如果是文本文件）
    if Path(script_path).suffix not in ['.exe', '.bin']:
        result['checks']['has_shebang'] = check_shebang(script_path)

    # 运行脚本
    run_result = run_script_safely(script_path, args)
    result['execution'] = run_result

    # 验证返回码
    if run_result['returncode'] == expected_returncode:
        result['checks']['returncode_match'] = True
    else:
        result['checks']['returncode_match'] = False
        result['errors'].append(
            f"Return code mismatch: expected {expected_returncode}, got {run_result['returncode']}"
        )

    # 验证输出内容
    if expected_output:
        if expected_output in run_result['stdout']:
            result['checks']['output_match'] = True
        else:
            result['checks']['output_match'] = False
            result['errors'].append(f"Expected output not found: {expected_output}")

    # 判断是否通过所有检查
    result['passed'] = all(result['checks'].values()) and not result['errors']

    return result


def main():
    parser = argparse.ArgumentParser(description='Verify script execution')
    parser.add_argument('script', help='Script path to verify')
    parser.add_argument('--expected-output', help='Expected output substring')
    parser.add_argument('--expected-returncode', type=int, default=0, help='Expected return code')
    parser.add_argument('--args', nargs='*', help='Arguments to pass to script')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')

    args = parser.parse_args()

    result = verify_script(
        args.script,
        expected_output=args.expected_output,
        expected_returncode=args.expected_returncode,
        args=args.args
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Script: {result['script']}")
        print(f"Passed: {result['passed']}")
        print(f"Checks:")
        for check, passed in result['checks'].items():
            print(f"  {check}: {'✓' if passed else '✗'}")
        if result['errors']:
            print(f"Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        if result['execution']:
            print(f"Execution:")
            print(f"  stdout: {result['execution']['stdout'][:500]}")
            print(f"  stderr: {result['execution']['stderr'][:500]}")

    sys.exit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
