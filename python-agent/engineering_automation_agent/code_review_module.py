#!/usr/bin/env python3
"""
Code Review and Deduplication Module
Automated code review capabilities with duplicate detection and cleanup recommendations
"""

import os
import ast
import re
import hashlib
import difflib
from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, Counter

from .core_agent import AgentModule, AgentConfig

@dataclass
class CodeIssue:
    """Represents a code quality issue"""
    type: str  # 'duplicate', 'complexity', 'style', 'security', 'performance'
    severity: str  # 'low', 'medium', 'high', 'critical'
    file_path: str
    line_number: int
    description: str
    suggestion: str = ""
    code_snippet: str = ""

@dataclass
class DuplicateCode:
    """Represents duplicate code blocks"""
    hash_value: str
    files: List[str] = field(default_factory=list)
    line_ranges: List[Tuple[int, int]] = field(default_factory=list)
    code_block: str = ""
    similarity_score: float = 0.0

@dataclass
class CodeMetrics:
    """Code quality metrics"""
    total_files: int = 0
    total_lines: int = 0
    duplicate_lines: int = 0
    complexity_score: float = 0.0
    maintainability_index: float = 0.0
    test_coverage: float = 0.0
    issues_count: Dict[str, int] = field(default_factory=dict)

class CodeReviewModule(AgentModule):
    """Automated code review and deduplication module"""
    
    def __init__(self, config: AgentConfig, logger):
        super().__init__(config, logger)
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go'}
        self.issues: List[CodeIssue] = []
        self.duplicates: List[DuplicateCode] = []
        self.metrics = CodeMetrics()
    
    def validate_config(self) -> bool:
        """Validate module configuration"""
        if not self.config.code_review_enabled:
            self.log_info("Code review disabled in configuration")
            return False
        
        if not os.path.exists(self.config.project_root):
            self.log_error(f"Project root does not exist: {self.config.project_root}")
            return False
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code review and deduplication analysis"""
        self.log_info("🔍 Starting code review and deduplication analysis")
        
        # Reset state
        self.issues.clear()
        self.duplicates.clear()
        self.metrics = CodeMetrics()
        
        # Analyze codebase
        source_files = self._find_source_files()
        self.log_info(f"📁 Found {len(source_files)} source files")
        
        # Perform analysis
        self._analyze_code_quality(source_files)
        self._detect_duplicates(source_files)
        self._calculate_metrics(source_files)
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Prepare results
        results = {
            'metrics': self.metrics.__dict__,
            'issues': [issue.__dict__ for issue in self.issues],
            'duplicates': [dup.__dict__ for dup in self.duplicates],
            'recommendations': recommendations,
            'summary': self._generate_summary()
        }
        
        self.log_info(f"✅ Code review completed: {len(self.issues)} issues, {len(self.duplicates)} duplicates found")
        return results
    
    def _find_source_files(self) -> List[str]:
        """Find all source code files in the project"""
        source_files = []
        
        for root, dirs, files in os.walk(self.config.project_root):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                '__pycache__', 'node_modules', 'build', 'dist', 'target', 'bin', 'obj'
            }]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.supported_extensions):
                    source_files.append(os.path.join(root, file))
        
        return source_files
    
    def _analyze_code_quality(self, source_files: List[str]):
        """Analyze code quality issues"""
        self.log_info("🔍 Analyzing code quality...")
        
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Analyze based on file type
                if file_path.endswith('.py'):
                    self._analyze_python_file(file_path, content)
                else:
                    self._analyze_generic_file(file_path, content)
                    
            except Exception as e:
                self.log_warning(f"Failed to analyze {file_path}: {str(e)}")
    
    def _analyze_python_file(self, file_path: str, content: str):
        """Analyze Python-specific code quality"""
        lines = content.split('\n')
        
        try:
            tree = ast.parse(content)
            
            # Check for complexity issues
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    if complexity > 10:
                        self.issues.append(CodeIssue(
                            type='complexity',
                            severity='high' if complexity > 15 else 'medium',
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Function '{node.name}' has high cyclomatic complexity: {complexity}",
                            suggestion="Consider breaking this function into smaller functions"
                        ))
                
                # Check for long functions
                if isinstance(node, ast.FunctionDef):
                    func_lines = getattr(node, 'end_lineno', node.lineno) - node.lineno
                    if func_lines > 50:
                        self.issues.append(CodeIssue(
                            type='style',
                            severity='medium',
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Function '{node.name}' is too long: {func_lines} lines",
                            suggestion="Consider breaking this function into smaller functions"
                        ))
        
        except SyntaxError as e:
            self.issues.append(CodeIssue(
                type='syntax',
                severity='critical',
                file_path=file_path,
                line_number=e.lineno or 1,
                description=f"Syntax error: {str(e)}",
                suggestion="Fix syntax error"
            ))
        
        # Check for common issues
        self._check_common_issues(file_path, lines)
    
    def _analyze_generic_file(self, file_path: str, content: str):
        """Analyze generic file for common issues"""
        lines = content.split('\n')
        self._check_common_issues(file_path, lines)
    
    def _check_common_issues(self, file_path: str, lines: List[str]):
        """Check for common code issues"""
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 120:
                self.issues.append(CodeIssue(
                    type='style',
                    severity='low',
                    file_path=file_path,
                    line_number=i,
                    description=f"Line too long: {len(line)} characters",
                    suggestion="Break long lines for better readability"
                ))
            
            # TODO comments
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                self.issues.append(CodeIssue(
                    type='maintenance',
                    severity='low',
                    file_path=file_path,
                    line_number=i,
                    description="TODO/FIXME comment found",
                    suggestion="Address TODO/FIXME comments",
                    code_snippet=line.strip()
                ))
            
            # Hardcoded credentials (basic check)
            if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                self.issues.append(CodeIssue(
                    type='security',
                    severity='high',
                    file_path=file_path,
                    line_number=i,
                    description="Potential hardcoded credential",
                    suggestion="Use environment variables or secure configuration"
                ))
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _detect_duplicates(self, source_files: List[str]):
        """Detect duplicate code blocks"""
        self.log_info("🔍 Detecting duplicate code...")
        
        code_blocks = defaultdict(list)
        
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                # Extract code blocks (functions, classes, etc.)
                blocks = self._extract_code_blocks(file_path, lines)
                
                for block in blocks:
                    # Normalize code for comparison
                    normalized = self._normalize_code(block['code'])
                    hash_value = hashlib.md5(normalized.encode()).hexdigest()
                    
                    code_blocks[hash_value].append({
                        'file': file_path,
                        'start_line': block['start_line'],
                        'end_line': block['end_line'],
                        'code': block['code']
                    })
                    
            except Exception as e:
                self.log_warning(f"Failed to analyze duplicates in {file_path}: {str(e)}")
        
        # Find duplicates
        for hash_value, blocks in code_blocks.items():
            if len(blocks) > 1:
                duplicate = DuplicateCode(
                    hash_value=hash_value,
                    files=[block['file'] for block in blocks],
                    line_ranges=[(block['start_line'], block['end_line']) for block in blocks],
                    code_block=blocks[0]['code'],
                    similarity_score=1.0
                )
                self.duplicates.append(duplicate)
    
    def _extract_code_blocks(self, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract meaningful code blocks from file"""
        blocks = []
        
        if file_path.endswith('.py'):
            # Extract Python functions and classes
            try:
                content = ''.join(lines)
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        start_line = node.lineno
                        end_line = getattr(node, 'end_lineno', start_line + 10)
                        
                        if end_line - start_line >= 5:  # Only consider blocks with 5+ lines
                            block_code = ''.join(lines[start_line-1:end_line])
                            blocks.append({
                                'start_line': start_line,
                                'end_line': end_line,
                                'code': block_code
                            })
            except:
                pass
        
        # Fallback: extract blocks based on indentation/braces
        if not blocks:
            blocks = self._extract_generic_blocks(lines)
        
        return blocks
    
    def _extract_generic_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract code blocks from any language based on patterns"""
        blocks = []
        current_block = []
        start_line = 0
        
        for i, line in enumerate(lines):
            if line.strip():
                if not current_block:
                    start_line = i + 1
                current_block.append(line)
            else:
                if len(current_block) >= 5:  # Minimum block size
                    blocks.append({
                        'start_line': start_line,
                        'end_line': i,
                        'code': ''.join(current_block)
                    })
                current_block = []
        
        # Handle last block
        if len(current_block) >= 5:
            blocks.append({
                'start_line': start_line,
                'end_line': len(lines),
                'code': ''.join(current_block)
            })
        
        return blocks
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison"""
        # Remove comments and whitespace
        lines = []
        for line in code.split('\n'):
            # Remove comments (basic)
            line = re.sub(r'#.*$', '', line)  # Python comments
            line = re.sub(r'//.*$', '', line)  # C-style comments
            
            # Normalize whitespace
            line = re.sub(r'\s+', ' ', line.strip())
            
            if line:
                lines.append(line)
        
        return '\n'.join(lines)
    
    def _calculate_metrics(self, source_files: List[str]):
        """Calculate overall code metrics"""
        self.metrics.total_files = len(source_files)
        
        total_lines = 0
        duplicate_lines = 0
        
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
            except:
                pass
        
        # Calculate duplicate lines
        for duplicate in self.duplicates:
            for start, end in duplicate.line_ranges:
                duplicate_lines += (end - start + 1)
        
        self.metrics.total_lines = total_lines
        self.metrics.duplicate_lines = duplicate_lines
        
        # Calculate issue counts
        issue_counts = Counter(issue.type for issue in self.issues)
        self.metrics.issues_count = dict(issue_counts)
        
        # Calculate quality scores
        if total_lines > 0:
            duplicate_ratio = duplicate_lines / total_lines
            issue_ratio = len(self.issues) / total_lines * 1000  # Issues per 1000 lines
            
            # Simple maintainability index (0-100)
            self.metrics.maintainability_index = max(0, 100 - (duplicate_ratio * 50) - (issue_ratio * 10))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate code improvement recommendations"""
        recommendations = []
        
        # Duplicate code recommendations
        if self.duplicates:
            recommendations.append(f"🔄 Found {len(self.duplicates)} duplicate code blocks. Consider extracting common functionality into reusable functions or modules.")
        
        # Issue-based recommendations
        issue_types = Counter(issue.type for issue in self.issues)
        
        if issue_types.get('complexity', 0) > 0:
            recommendations.append(f"🧩 {issue_types['complexity']} functions have high complexity. Break them into smaller, more focused functions.")
        
        if issue_types.get('security', 0) > 0:
            recommendations.append(f"🔒 {issue_types['security']} potential security issues found. Review and address immediately.")
        
        if issue_types.get('style', 0) > 0:
            recommendations.append(f"✨ {issue_types['style']} style issues found. Consider using a code formatter and linter.")
        
        # Maintainability recommendations
        if self.metrics.maintainability_index < 70:
            recommendations.append("📈 Code maintainability is below recommended threshold. Focus on reducing complexity and duplicates.")
        
        return recommendations
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate analysis summary"""
        return {
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i.severity == 'critical']),
            'high_issues': len([i for i in self.issues if i.severity == 'high']),
            'duplicate_blocks': len(self.duplicates),
            'maintainability_score': round(self.metrics.maintainability_index, 2),
            'quality_grade': self._get_quality_grade()
        }
    
    def _get_quality_grade(self) -> str:
        """Get overall quality grade"""
        score = self.metrics.maintainability_index
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
