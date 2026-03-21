#!/usr/bin/env python3
"""
secrets_scanner.py - 敏感信息检测脚本

基于 SECURITY_CHECK.md 文档实现，用于检测代码库中的敏感信息泄露风险。
"""

import os
import re
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field, asdict


@dataclass
class Finding:
    """检测结果"""
    category: str
    severity: str  # high, medium, low
    file: str
    line: int
    description: str
    match: str = ""
    recommendation: str = ""


@dataclass
class ScanResult:
    """扫描结果"""
    findings: List[Finding] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "findings": [asdict(f) for f in self.findings],
            "stats": self.stats
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class SecretsScanner:
    """敏感信息扫描器"""
    
    SENSITIVE_FILE_PATTERNS = [
        r'\.env$',
        r'\.env\.local$',
        r'\.env\..*\.local$',
        r'secret',
        r'password',
        r'credential',
        r'\.pem$',
        r'\.key$',
        r'\.p12$',
        r'\.pfx$',
        r'\.keystore$',
        r'id_rsa$',
        r'id_ed25519$',
        r'credentials\.json$',
        r'secrets\.ya?ml$',
    ]
    
    KEYWORD_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*[\'"]?[\w-]{20,}[\'"]?', 'API密钥'),
        (r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*[\'"]?[\w-]{16,}[\'"]?', '密钥'),
        (r'(?i)(private[_-]?key|privatekey)\s*[=:]\s*[\'"]?[\w-]{16,}[\'"]?', '私钥'),
        (r'(?i)(access[_-]?token|accesstoken)\s*[=:]\s*[\'"]?[\w-]{16,}[\'"]?', '访问令牌'),
        (r'(?i)(refresh[_-]?token|refreshtoken)\s*[=:]\s*[\'"]?[\w-]{16,}[\'"]?', '刷新令牌'),
        (r'(?i)(auth[_-]?token|authtoken)\s*[=:]\s*[\'"]?[\w-]{16,}[\'"]?', '认证令牌'),
        (r'(?i)(password|passwd|pwd)\s*[=:]\s*[\'"]?[^\'"}\s]{8,}[\'"]?', '密码'),
        (r'(?i)Bearer\s+[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', 'Bearer Token'),
    ]
    
    SECRET_FORMAT_PATTERNS = [
        (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
        (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Token'),
        (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', 'GitHub PAT'),
        (r'AIza[0-9A-Za-z_-]{35}', 'Google API Key'),
        (r'xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}', 'Slack Token'),
        (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', 'JWT Token'),
        (r'sk-[a-zA-Z0-9]{32,}', 'OpenAI API Key'),
    ]
    
    PRIVATE_KEY_PATTERNS = [
        r'-----BEGIN RSA PRIVATE KEY-----',
        r'-----BEGIN OPENSSH PRIVATE KEY-----',
        r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        r'-----BEGIN EC PRIVATE KEY-----',
        r'-----BEGIN PRIVATE KEY-----',
    ]
    
    DB_CONNECTION_PATTERNS = [
        (r'mongodb(\+srv)?://[^:]+:[^@]+@[^/]+', 'MongoDB连接串'),
        (r'mysql://[^:]+:[^@]+@[^/]+', 'MySQL连接串'),
        (r'postgres(ql)?://[^:]+:[^@]+@[^/]+', 'PostgreSQL连接串'),
        (r'redis://:[^@]+@[^/]+', 'Redis连接串'),
    ]
    
    IGNORE_DIRS = {
        'node_modules', '.venv', 'venv', '__pycache__', '.git',
        'dist', 'build', '.tox', 'egg-info', '.mypy_cache', '.pytest_cache',
        'tests', 'test', 'spec', 'specs', 'mocks', 'fixtures'
    }
    
    IGNORE_FILE_SUFFIXES = {
        '.example', '.sample', '.template', '.mock', '.fixture'
    }
    
    def __init__(self, target_path: str = ".", output_json: bool = False):
        self.target_path = Path(target_path).resolve()
        self.output_json = output_json
        self.result = ScanResult()
        
    def _should_ignore_path(self, path: Path) -> bool:
        """检查路径是否应该被忽略"""
        parts = path.parts
        for part in parts:
            if part in self.IGNORE_DIRS:
                return True
        
        filename = path.name.lower()
        for suffix in self.IGNORE_FILE_SUFFIXES:
            if filename.endswith(suffix):
                return True
        
        return False
    
    def _run_git_command(self, args: List[str]) -> Tuple[str, bool]:
        """执行git命令"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.target_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip(), result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "", False
    
    def scan_tracked_sensitive_files(self) -> List[Finding]:
        """检查已跟踪的敏感文件"""
        findings = []
        output, success = self._run_git_command(['ls-files'])
        
        if not success or not output:
            return findings
        
        for line in output.split('\n'):
            if not line:
                continue
            filename = os.path.basename(line)
            for pattern in self.SENSITIVE_FILE_PATTERNS:
                if re.search(pattern, filename, re.IGNORECASE):
                    findings.append(Finding(
                        category="tracked_sensitive_files",
                        severity="high",
                        file=line,
                        line=0,
                        description=f"敏感文件已被git跟踪: {filename}",
                        match=filename,
                        recommendation="将此文件添加到.gitignore并从git历史中移除"
                    ))
                    break
        
        return findings
    
    def scan_gitignore(self) -> List[Finding]:
        """检查.gitignore配置"""
        findings = []
        gitignore_path = self.target_path / '.gitignore'
        
        required_patterns = ['.env', '*.pem', '*.key']
        
        if not gitignore_path.exists():
            findings.append(Finding(
                category="gitignore_config",
                severity="medium",
                file=".gitignore",
                line=0,
                description=".gitignore文件不存在",
                recommendation="创建.gitignore文件并添加敏感文件模式"
            ))
            return findings
        
        try:
            content = gitignore_path.read_text()
            for pattern in required_patterns:
                if pattern not in content:
                    findings.append(Finding(
                        category="gitignore_config",
                        severity="medium",
                        file=".gitignore",
                        line=0,
                        description=f".gitignore中缺少敏感文件模式: {pattern}",
                        recommendation=f"在.gitignore中添加 {pattern}"
                    ))
        except Exception as e:
            findings.append(Finding(
                category="gitignore_config",
                severity="low",
                file=".gitignore",
                line=0,
                description=f"无法读取.gitignore: {str(e)}",
                recommendation="检查.gitignore文件权限"
            ))
        
        return findings
    
    def scan_code_for_keywords(self) -> List[Finding]:
        """检查代码中的敏感关键词"""
        findings = []
        
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php', '.yaml', '.yml', '.json', '.sh'}
        
        for filepath in self.target_path.rglob('*'):
            if not filepath.is_file():
                continue
            if self._should_ignore_path(filepath):
                continue
            if filepath.suffix not in code_extensions:
                continue
            
            try:
                content = filepath.read_text(errors='ignore')
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, desc in self.KEYWORD_PATTERNS:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            findings.append(Finding(
                                category="sensitive_keywords",
                                severity="high",
                                file=str(filepath.relative_to(self.target_path)),
                                line=line_num,
                                description=f"发现{desc}",
                                match=match.group()[:50] + "..." if len(match.group()) > 50 else match.group(),
                                recommendation="将敏感信息移至环境变量或密钥管理服务"
                            ))
                    
                    for pattern, desc in self.DB_CONNECTION_PATTERNS:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            findings.append(Finding(
                                category="database_connection",
                                severity="high",
                                file=str(filepath.relative_to(self.target_path)),
                                line=line_num,
                                description=f"发现{desc}(可能包含密码)",
                                match="[已隐藏敏感信息]",
                                recommendation="使用环境变量存储连接字符串"
                            ))
            except Exception:
                pass
        
        return findings
    
    def scan_secret_formats(self) -> List[Finding]:
        """检查潜在的密钥格式"""
        findings = []
        
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php', '.yaml', '.yml', '.json', '.sh', '.env'}
        
        for filepath in self.target_path.rglob('*'):
            if not filepath.is_file():
                continue
            if self._should_ignore_path(filepath):
                continue
            if filepath.suffix not in code_extensions:
                continue
            
            try:
                content = filepath.read_text(errors='ignore')
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, desc in self.SECRET_FORMAT_PATTERNS:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            findings.append(Finding(
                                category="secret_formats",
                                severity="high",
                                file=str(filepath.relative_to(self.target_path)),
                                line=line_num,
                                description=f"发现{desc}",
                                match="[已隐藏敏感信息]",
                                recommendation="立即轮换此密钥并从代码中移除"
                            ))
                    
                    for pattern in self.PRIVATE_KEY_PATTERNS:
                        if pattern in line:
                            findings.append(Finding(
                                category="private_keys",
                                severity="critical",
                                file=str(filepath.relative_to(self.target_path)),
                                line=line_num,
                                description="发现私钥内容",
                                match="[已隐藏敏感信息]",
                                recommendation="立即从代码中移除私钥，使用密钥管理服务"
                            ))
            except Exception:
                pass
        
        return findings
    
    def scan_git_history(self) -> List[Finding]:
        """检查git历史中的敏感文件"""
        findings = []
        
        sensitive_patterns = ['*.env', '.env.local', '*.pem', '*.key', '*.keystore', 'id_rsa', 'id_ed25519']
        
        for pattern in sensitive_patterns:
            output, success = self._run_git_command(['log', '--all', '--full-history', '--oneline', '--', pattern])
            if success and output:
                lines = output.strip().split('\n')
                if lines and lines[0]:
                    findings.append(Finding(
                        category="git_history",
                        severity="medium",
                        file=pattern,
                        line=0,
                        description=f"git历史中发现敏感文件: {pattern}",
                        match=f"发现 {len(lines)} 个提交",
                        recommendation="使用git filter-repo或BFG从历史中移除"
                    ))
        
        return findings
    
    def scan(self) -> ScanResult:
        """执行完整扫描"""
        print("=== 敏感信息检测 ===\n", file=sys.stderr)
        
        print("[1/5] 检查已跟踪的敏感文件...", file=sys.stderr)
        self.result.findings.extend(self.scan_tracked_sensitive_files())
        
        print("[2/5] 检查.gitignore配置...", file=sys.stderr)
        self.result.findings.extend(self.scan_gitignore())
        
        print("[3/5] 检查代码中的敏感关键词...", file=sys.stderr)
        self.result.findings.extend(self.scan_code_for_keywords())
        
        print("[4/5] 检查潜在的密钥格式...", file=sys.stderr)
        self.result.findings.extend(self.scan_secret_formats())
        
        print("[5/5] 检查git历史中的敏感文件...", file=sys.stderr)
        self.result.findings.extend(self.scan_git_history())
        
        self.result.stats = {
            "total_findings": len(self.result.findings),
            "critical": len([f for f in self.result.findings if f.severity == "critical"]),
            "high": len([f for f in self.result.findings if f.severity == "high"]),
            "medium": len([f for f in self.result.findings if f.severity == "medium"]),
            "low": len([f for f in self.result.findings if f.severity == "low"]),
        }
        
        return self.result
    
    def print_report(self):
        """打印报告"""
        print("\n=== 扫描报告 ===\n")
        
        if not self.result.findings:
            print("✓ 未发现敏感信息泄露风险\n")
            return
        
        severity_colors = {
            "critical": "\033[91m",
            "high": "\033[93m",
            "medium": "\033[94m",
            "low": "\033[90m",
        }
        reset_color = "\033[0m"
        
        for finding in sorted(self.result.findings, key=lambda f: ["critical", "high", "medium", "low"].index(f.severity)):
            color = severity_colors.get(finding.severity, "")
            print(f"{color}[{finding.severity.upper()}]{reset_color} {finding.category}")
            print(f"  文件: {finding.file}:{finding.line}")
            print(f"  描述: {finding.description}")
            if finding.match:
                print(f"  匹配: {finding.match}")
            print(f"  建议: {finding.recommendation}")
            print()
        
        print("=== 统计信息 ===")
        print(f"总计: {self.result.stats['total_findings']} 个问题")
        print(f"  严重: {self.result.stats['critical']}")
        print(f"  高危: {self.result.stats['high']}")
        print(f"  中危: {self.result.stats['medium']}")
        print(f"  低危: {self.result.stats['low']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='敏感信息扫描工具')
    parser.add_argument('path', nargs='?', default='.', help='要扫描的目录路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式，仅输出结果')
    
    args = parser.parse_args()
    
    scanner = SecretsScanner(args.path, output_json=args.json)
    result = scanner.scan()
    
    if args.json:
        print(result.to_json())
    else:
        scanner.print_report()
    
    sys.exit(result.stats['total_findings'] > 0)


if __name__ == '__main__':
    main()