#!/usr/bin/env python3
"""
Code Review and Deduplication Tool
Analyzes codebase for quality issues, duplicated code, and provides refactoring recommendations
"""

import os
import ast
import hashlib
import difflib
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json

from utils import FileHelper, StatusIconHelper
from messages import get_message


@dataclass
class CodeIssue:
    """Represents a code quality issue"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    suggestion: str = ""


@dataclass
class DuplicateBlock:
    """Represents a duplicate code block"""
    files: List[str]
    lines: List[Tuple[int, int]]  # (start_line, end_line) for each file
    similarity: float
    content: str


class CodeAnalyzer:
    """Analyzes Python code for quality issues and duplicates"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.issues: List[CodeIssue] = []
        self.duplicates: List[DuplicateBlock] = []
        self.metrics: Dict[str, Any] = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive code analysis"""
        print(f"🔍 {get_message('code_review_starting')}")
        
        # Find all Python files
        python_files = self._find_python_files()
        
        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)
        
        # Find duplicates
        self._find_duplicates(python_files)
        
        # Calculate metrics
        self._calculate_metrics(python_files)
        
        print(f"✅ {get_message('code_review_completed')}")
        print(f"📊 {get_message('code_review_issues_found', count=len(self.issues))}")
        print(f"🔄 {get_message('code_review_duplicates_found', count=len(self.duplicates))}")
        
        return {
            'issues': [self._issue_to_dict(issue) for issue in self.issues],
            'duplicates': [self._duplicate_to_dict(dup) for dup in self.duplicates],
            'metrics': self.metrics
        }
    
    def _find_python_files(self) -> List[str]:
        """Find all Python files in the project"""
        python_files = []
        for root, dirs, files in os.walk(self.project_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'venv', 'env'}]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _analyze_file(self, file_path: str):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    issue_type="syntax_error",
                    severity="error",
                    description=f"Syntax error: {e.msg}",
                    suggestion="Fix syntax error"
                ))
                return
            
            # Analyze AST
            self._analyze_ast(file_path, tree, content.split('\n'))
            
        except Exception as e:
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=0,
                issue_type="file_error",
                severity="error",
                description=f"Could not analyze file: {str(e)}",
                suggestion="Check file encoding and permissions"
            ))
    
    def _analyze_ast(self, file_path: str, tree: ast.AST, lines: List[str]):
        """Analyze AST for code quality issues"""
        
        class CodeVisitor(ast.NodeVisitor):
            def __init__(self, analyzer, file_path, lines):
                self.analyzer = analyzer
                self.file_path = file_path
                self.lines = lines
                self.function_complexity = defaultdict(int)
                self.class_methods = defaultdict(list)
            
            def visit_FunctionDef(self, node):
                # Check function length
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        self.analyzer.issues.append(CodeIssue(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            issue_type="long_function",
                            severity="warning",
                            description=f"Function '{node.name}' is {func_length} lines long",
                            suggestion="Consider breaking into smaller functions"
                        ))
                
                # Check for missing docstring
                if not ast.get_docstring(node):
                    self.analyzer.issues.append(CodeIssue(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        issue_type="missing_docstring",
                        severity="info",
                        description=f"Function '{node.name}' missing docstring",
                        suggestion="Add docstring to document function purpose"
                    ))
                
                # Check parameter count
                if len(node.args.args) > 7:
                    self.analyzer.issues.append(CodeIssue(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        issue_type="too_many_parameters",
                        severity="warning",
                        description=f"Function '{node.name}' has {len(node.args.args)} parameters",
                        suggestion="Consider using a configuration object or reducing parameters"
                    ))
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check for missing docstring
                if not ast.get_docstring(node):
                    self.analyzer.issues.append(CodeIssue(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        issue_type="missing_docstring",
                        severity="info",
                        description=f"Class '{node.name}' missing docstring",
                        suggestion="Add docstring to document class purpose"
                    ))
                
                # Count methods
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:
                    self.analyzer.issues.append(CodeIssue(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        issue_type="large_class",
                        severity="warning",
                        description=f"Class '{node.name}' has {len(methods)} methods",
                        suggestion="Consider breaking into smaller classes"
                    ))
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for unused imports (basic check)
                for alias in node.names:
                    import_name = alias.name
                    if import_name not in ' '.join(self.lines):
                        self.analyzer.issues.append(CodeIssue(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            issue_type="unused_import",
                            severity="info",
                            description=f"Potentially unused import: {import_name}",
                            suggestion="Remove unused import"
                        ))
                
                self.generic_visit(node)
        
        visitor = CodeVisitor(self, file_path, lines)
        visitor.visit(tree)
    
    def _find_duplicates(self, python_files: List[str]):
        """Find duplicate code blocks"""
        print(f"🔄 {get_message('deduplication_starting')}")
        
        # Simple duplicate detection based on function signatures and content
        function_hashes = defaultdict(list)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                lines = content.split('\n')
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Get function content
                        if hasattr(node, 'end_lineno') and node.end_lineno:
                            func_lines = lines[node.lineno-1:node.end_lineno]
                            func_content = '\n'.join(func_lines)
                            
                            # Create hash of normalized content
                            normalized = self._normalize_code(func_content)
                            content_hash = hashlib.md5(normalized.encode()).hexdigest()
                            
                            function_hashes[content_hash].append({
                                'file': file_path,
                                'name': node.name,
                                'start_line': node.lineno,
                                'end_line': node.end_lineno,
                                'content': func_content
                            })
            
            except Exception:
                continue
        
        # Find duplicates
        for content_hash, functions in function_hashes.items():
            if len(functions) > 1:
                self.duplicates.append(DuplicateBlock(
                    files=[f['file'] for f in functions],
                    lines=[(f['start_line'], f['end_line']) for f in functions],
                    similarity=1.0,  # Exact match
                    content=functions[0]['content'][:200] + "..." if len(functions[0]['content']) > 200 else functions[0]['content']
                ))
        
        print(f"✅ {get_message('deduplication_completed')}")
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison"""
        # Remove comments and normalize whitespace
        lines = []
        for line in code.split('\n'):
            # Remove comments
            if '#' in line:
                line = line[:line.index('#')]
            # Normalize whitespace
            line = ' '.join(line.split())
            if line:
                lines.append(line)
        return '\n'.join(lines)
    
    def _calculate_metrics(self, python_files: List[str]):
        """Calculate code metrics"""
        total_lines = 0
        total_files = len(python_files)
        duplicate_lines = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
            except Exception:
                continue
        
        # Calculate duplicate lines
        for duplicate in self.duplicates:
            for start_line, end_line in duplicate.lines:
                duplicate_lines += (end_line - start_line + 1)
        
        # Calculate maintainability index (simplified)
        issue_density = len(self.issues) / total_files if total_files > 0 else 0
        duplicate_ratio = duplicate_lines / total_lines if total_lines > 0 else 0
        maintainability_index = max(0, 100 - (issue_density * 10) - (duplicate_ratio * 50))
        
        self.metrics = {
            'total_files': total_files,
            'total_lines': total_lines,
            'duplicate_lines': duplicate_lines,
            'duplicate_ratio': duplicate_ratio * 100,
            'issue_count': len(self.issues),
            'issue_density': issue_density,
            'maintainability_index': maintainability_index
        }
        
        print(f"📊 {get_message('code_review_metrics_calculated')}")
    
    def _issue_to_dict(self, issue: CodeIssue) -> Dict[str, Any]:
        """Convert CodeIssue to dictionary"""
        return {
            'file_path': issue.file_path,
            'line_number': issue.line_number,
            'type': issue.issue_type,
            'severity': issue.severity,
            'description': issue.description,
            'suggestion': issue.suggestion
        }
    
    def _duplicate_to_dict(self, duplicate: DuplicateBlock) -> Dict[str, Any]:
        """Convert DuplicateBlock to dictionary"""
        return {
            'files': duplicate.files,
            'lines': duplicate.lines,
            'similarity': duplicate.similarity,
            'content_preview': duplicate.content
        }


def main():
    """Main function for standalone execution"""
    import sys
    
    project_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    analyzer = CodeAnalyzer(project_path)
    results = analyzer.analyze_project()
    
    # Save results
    output_file = 'code_review_results.json'
    if FileHelper.write_json_file(output_file, results):
        print(f"📄 Results saved to {output_file}")
    else:
        print("❌ Failed to save results")
    
    return results


if __name__ == "__main__":
    main()
