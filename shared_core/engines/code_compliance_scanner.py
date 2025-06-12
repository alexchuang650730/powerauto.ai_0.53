#!/usr/bin/env python3
"""
PowerAutomation 代码与目录规范扫描模块

实现功能：
1. 目录结构规范检查
2. 文件命名规范检查
3. 代码风格规范检查
4. manus相关字眼检测
"""

import os
import re
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("code_compliance_scanner")

@dataclass
class ScannerConfig:
    """扫描器配置"""
    # 目录结构规范
    directory_structure: Dict[str, List[str]] = None
    
    # 文件命名规范
    file_naming_patterns: Dict[str, str] = None
    
    # 代码风格规范
    code_style_rules: Dict[str, Any] = None
    
    # 忽略的路径
    ignored_paths: List[str] = None
    
    # manus引用检测
    detect_manus_references: bool = True
    
    def __post_init__(self):
        if self.directory_structure is None:
            self.directory_structure = {
                "src": ["core", "utils", "models"],
                "tests": ["unit", "integration"],
                "docs": ["api", "user_guides"]
            }
        
        if self.file_naming_patterns is None:
            self.file_naming_patterns = {
                "python": r"^[a-z][a-z0-9_]*\.py$",
                "javascript": r"^[a-z][a-zA-Z0-9_]*\.js$",
                "typescript": r"^[a-z][a-zA-Z0-9_]*\.ts$",
                "markdown": r"^[A-Z][a-zA-Z0-9_]*\.md$"
            }
        
        if self.code_style_rules is None:
            self.code_style_rules = {
                "python": {
                    "class_naming": r"^[A-Z][a-zA-Z0-9]*$",
                    "function_naming": r"^[a-z][a-z0-9_]*$",
                    "variable_naming": r"^[a-z][a-z0-9_]*$",
                    "constant_naming": r"^[A-Z][A-Z0-9_]*$",
                    "max_line_length": 100,
                    "indentation": 4
                },
                "javascript": {
                    "class_naming": r"^[A-Z][a-zA-Z0-9]*$",
                    "function_naming": r"^[a-z][a-zA-Z0-9]*$",
                    "variable_naming": r"^[a-z][a-zA-Z0-9]*$",
                    "constant_naming": r"^[A-Z][A-Z0-9_]*$",
                    "max_line_length": 100,
                    "indentation": 2
                }
            }
        
        if self.ignored_paths is None:
            self.ignored_paths = [
                ".git", "node_modules", "venv", "__pycache__",
                "build", "dist", ".vscode", ".idea"
            ]

class CodeComplianceScanner:
    """代码与目录规范扫描器"""
    
    def __init__(self, config: Optional[ScannerConfig] = None):
        self.config = config or ScannerConfig()
        self.issues = []
        self.stats = {
            "files_scanned": 0,
            "directories_scanned": 0,
            "issues_found": 0,
            "issue_types": {}
        }
    
    def scan(self, path: str) -> List[Dict[str, Any]]:
        """扫描指定路径的代码与目录规范"""
        self.issues = []
        self.stats = {
            "files_scanned": 0,
            "directories_scanned": 0,
            "issues_found": 0,
            "issue_types": {}
        }
        
        if not os.path.exists(path):
            logger.error(f"路径不存在: {path}")
            return []
        
        logger.info(f"开始扫描: {path}")
        
        # 检查目录结构
        self._scan_directory_structure(path)
        
        # 扫描文件
        self._scan_files(path)
        
        # 更新统计信息
        self.stats["issues_found"] = len(self.issues)
        
        logger.info(f"扫描完成: 发现 {len(self.issues)} 个问题")
        return self.issues
    
    def _scan_directory_structure(self, path: str):
        """检查目录结构是否符合规范"""
        expected_structure = self.config.directory_structure
        
        for parent_dir, expected_subdirs in expected_structure.items():
            parent_path = os.path.join(path, parent_dir)
            
            if not os.path.isdir(parent_path):
                self._add_issue(
                    issue_type="directory_structure",
                    severity="warning",
                    message=f"缺少规范目录: {parent_dir}",
                    path=parent_path
                )
                continue
            
            self.stats["directories_scanned"] += 1
            
            for subdir in expected_subdirs:
                subdir_path = os.path.join(parent_path, subdir)
                if not os.path.isdir(subdir_path):
                    self._add_issue(
                        issue_type="directory_structure",
                        severity="warning",
                        message=f"缺少规范子目录: {parent_dir}/{subdir}",
                        path=subdir_path
                    )
    
    def _scan_files(self, path: str):
        """扫描文件规范"""
        for root, dirs, files in os.walk(path):
            # 跳过忽略的目录
            dirs[:] = [d for d in dirs if d not in self.config.ignored_paths]
            
            self.stats["directories_scanned"] += 1
            
            for file in files:
                file_path = os.path.join(root, file)
                self._scan_file(file_path)
    
    def _scan_file(self, file_path: str):
        """扫描单个文件"""
        self.stats["files_scanned"] += 1
        
        # 检查文件命名
        self._check_file_naming(file_path)
        
        # 检查文件内容
        self._check_file_content(file_path)
    
    def _check_file_naming(self, file_path: str):
        """检查文件命名是否符合规范"""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 根据文件扩展名确定文件类型
        file_type = None
        if file_ext == ".py":
            file_type = "python"
        elif file_ext == ".js":
            file_type = "javascript"
        elif file_ext == ".ts":
            file_type = "typescript"
        elif file_ext == ".md":
            file_type = "markdown"
        
        if file_type and file_type in self.config.file_naming_patterns:
            pattern = self.config.file_naming_patterns[file_type]
            if not re.match(pattern, file_name):
                self._add_issue(
                    issue_type="file_naming",
                    severity="warning",
                    message=f"文件命名不符合规范: {file_name}",
                    path=file_path,
                    expected_pattern=pattern
                )
    
    def _check_file_content(self, file_path: str):
        """检查文件内容是否符合规范"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 确定文件类型
        file_type = None
        if file_ext == ".py":
            file_type = "python"
        elif file_ext == ".js":
            file_type = "javascript"
        elif file_ext == ".ts":
            file_type = "typescript"
        
        # 只检查支持的文件类型
        if file_type not in self.config.code_style_rules:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                
                # 检查代码风格
                self._check_code_style(file_path, file_type, content, lines)
                
                # 检查manus引用
                if self.config.detect_manus_references:
                    self._check_manus_references(file_path, content, lines)
                
        except Exception as e:
            logger.error(f"检查文件失败 {file_path}: {e}")
    
    def _check_code_style(self, file_path: str, file_type: str, content: str, lines: List[str]):
        """检查代码风格"""
        rules = self.config.code_style_rules[file_type]
        
        # 检查行长度
        max_line_length = rules.get("max_line_length", 100)
        for i, line in enumerate(lines):
            if len(line) > max_line_length:
                self._add_issue(
                    issue_type="line_length",
                    severity="info",
                    message=f"行长度超过{max_line_length}个字符",
                    path=file_path,
                    line=i + 1,
                    line_content=line
                )
        
        # 检查缩进
        indentation = rules.get("indentation")
        if indentation:
            for i, line in enumerate(lines):
                if line.strip() and line.startswith(" "):
                    indent_count = len(line) - len(line.lstrip(" "))
                    if indent_count % indentation != 0:
                        self._add_issue(
                            issue_type="indentation",
                            severity="info",
                            message=f"缩进不是{indentation}的倍数",
                            path=file_path,
                            line=i + 1,
                            line_content=line
                        )
        
        # 检查命名规范
        if file_type == "python":
            # 类命名
            class_pattern = rules.get("class_naming")
            if class_pattern:
                for match in re.finditer(r'class\s+(\w+)', content):
                    class_name = match.group(1)
                    if not re.match(class_pattern, class_name):
                        line_number = content[:match.start()].count('\n') + 1
                        self._add_issue(
                            issue_type="class_naming",
                            severity="warning",
                            message=f"类命名不符合规范: {class_name}",
                            path=file_path,
                            line=line_number,
                            expected_pattern=class_pattern
                        )
            
            # 函数命名
            function_pattern = rules.get("function_naming")
            if function_pattern:
                for match in re.finditer(r'def\s+(\w+)', content):
                    function_name = match.group(1)
                    # 跳过魔术方法
                    if function_name.startswith("__") and function_name.endswith("__"):
                        continue
                    
                    if not re.match(function_pattern, function_name):
                        line_number = content[:match.start()].count('\n') + 1
                        self._add_issue(
                            issue_type="function_naming",
                            severity="warning",
                            message=f"函数命名不符合规范: {function_name}",
                            path=file_path,
                            line=line_number,
                            expected_pattern=function_pattern
                        )
        
        elif file_type in ["javascript", "typescript"]:
            # 类命名
            class_pattern = rules.get("class_naming")
            if class_pattern:
                for match in re.finditer(r'class\s+(\w+)', content):
                    class_name = match.group(1)
                    if not re.match(class_pattern, class_name):
                        line_number = content[:match.start()].count('\n') + 1
                        self._add_issue(
                            issue_type="class_naming",
                            severity="warning",
                            message=f"类命名不符合规范: {class_name}",
                            path=file_path,
                            line=line_number,
                            expected_pattern=class_pattern
                        )
            
            # 函数命名
            function_pattern = rules.get("function_naming")
            if function_pattern:
                for match in re.finditer(r'function\s+(\w+)', content):
                    function_name = match.group(1)
                    if not re.match(function_pattern, function_name):
                        line_number = content[:match.start()].count('\n') + 1
                        self._add_issue(
                            issue_type="function_naming",
                            severity="warning",
                            message=f"函数命名不符合规范: {function_name}",
                            path=file_path,
                            line=line_number,
                            expected_pattern=function_pattern
                        )
    
    def _check_manus_references(self, file_path: str, content: str, lines: List[str]):
        """检查manus引用"""
        for match in re.finditer(r'\bmanus\b', content, re.IGNORECASE):
            line_number = content[:match.start()].count('\n') + 1
            line_content = lines[line_number - 1] if line_number <= len(lines) else ""
            
            self._add_issue(
                issue_type="manus_reference",
                severity="error",
                message=f"发现manus相关字眼",
                path=file_path,
                line=line_number,
                line_content=line_content,
                context=content[max(0, match.start()-20):min(len(content), match.end()+20)]
            )
    
    def _add_issue(self, issue_type: str, severity: str, message: str, path: str, **kwargs):
        """添加问题"""
        issue = {
            "type": issue_type,
            "severity": severity,
            "message": message,
            "path": path,
            **kwargs
        }
        
        self.issues.append(issue)
        
        # 更新统计信息
        if issue_type not in self.stats["issue_types"]:
            self.stats["issue_types"][issue_type] = 0
        self.stats["issue_types"][issue_type] += 1
    
    def generate_report(self, format_type: str = "text") -> str:
        """生成报告"""
        if format_type == "json":
            return json.dumps({
                "issues": self.issues,
                "stats": self.stats
            }, indent=2)
        
        # 默认文本格式
        report = []
        report.append("# 代码与目录规范扫描报告")
        report.append("")
        report.append(f"扫描文件数: {self.stats['files_scanned']}")
        report.append(f"扫描目录数: {self.stats['directories_scanned']}")
        report.append(f"发现问题数: {self.stats['issues_found']}")
        report.append("")
        
        # 按类型分组
        issues_by_type = {}
        for issue in self.issues:
            issue_type = issue["type"]
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # 生成报告
        for issue_type, type_issues in issues_by_type.items():
            report.append(f"## {issue_type.replace('_', ' ').title()} ({len(type_issues)})")
            report.append("")
            
            for issue in type_issues:
                severity = issue.get("severity", "info").upper()
                message = issue.get("message", "未知问题")
                path = issue.get("path", "")
                line = issue.get("line", "")
                
                location = path
                if line:
                    location += f":{line}"
                
                report.append(f"- [{severity}] {message}")
                report.append(f"  位置: {location}")
                
                # 如果有行内容，添加到报告
                if "line_content" in issue:
                    line_content = issue["line_content"].strip()
                    report.append(f"  代码: `{line_content}`")
                
                # 如果有上下文，添加到报告
                if "context" in issue:
                    context = issue["context"].replace("\n", " ")
                    report.append(f"  上下文: `{context}`")
                
                # 如果有期望模式，添加到报告
                if "expected_pattern" in issue:
                    report.append(f"  期望模式: `{issue['expected_pattern']}`")
                
                report.append("")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation 代码与目录规范扫描工具")
    parser.add_argument("path", help="要扫描的路径")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="报告格式")
    parser.add_argument("--output", help="报告输出文件路径")
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            config = ScannerConfig(**config_data)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return 1
    
    # 创建扫描器
    scanner = CodeComplianceScanner(config)
    
    # 扫描代码
    issues = scanner.scan(args.path)
    
    # 生成报告
    report = scanner.generate_report(args.format)
    
    # 输出报告
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {args.output}")
        except Exception as e:
            print(f"保存报告失败: {e}")
            return 1
    else:
        print(report)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
