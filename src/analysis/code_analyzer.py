import ast
from typing import Dict, List, Optional


class CodeAnalyzer:
    def analyze(self, code: str) -> Dict:
        """Perform static code analysis"""
        try:
            tree = ast.parse(code)
            return {
                "syntax_check": self._check_syntax(tree),
                "complexity": self._analyze_complexity(tree),
                "patterns": self._identify_patterns(tree),
                "imports": self._analyze_imports(tree),
                "potential_issues": self._find_potential_issues(tree)
            }
        except SyntaxError as e:
            return {
                "error": "syntax_error",
                "message": str(e),
                "line": e.lineno,
                "offset": e.offset
            }
        except Exception as e:
            return {
                "error": "analysis_error",
                "message": str(e)
            }

    def _check_syntax(self, tree: ast.AST) -> Dict:
        """Check for syntax issues"""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Check for bare except clauses
                for handler in node.handlers:
                    if handler.type is None:
                        issues.append({
                            "type": "bare_except",
                            "line": handler.lineno,
                            "message": "Avoid using bare 'except' clauses"
                        })
            elif isinstance(node, ast.Compare):
                # Check for potential type comparison issues
                if isinstance(node.ops[0], (ast.Is, ast.IsNot)):
                    issues.append({
                        "type": "type_comparison",
                        "line": node.lineno,
                        "message": "Use '==' instead of 'is' for value comparison"
                    })
        return {"issues": issues}

    def _analyze_complexity(self, tree: ast.AST) -> Dict:
        """Analyze code complexity"""
        complexity = {
            "loops": 0,
            "branches": 0,
            "nested_depth": 0,
            "function_count": 0
        }

        current_depth = 0
        max_depth = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                complexity["loops"] += 1
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif isinstance(node, ast.If):
                complexity["branches"] += 1
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif isinstance(node, ast.FunctionDef):
                complexity["function_count"] += 1

        complexity["nested_depth"] = max_depth
        return complexity

    def _identify_patterns(self, tree: ast.AST) -> List[Dict]:
        """Identify common code patterns"""
        patterns = []

        # Check for resource management patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                patterns.append({
                    "type": "resource_management",
                    "line": node.lineno,
                    "description": "Resource management using context manager"
                })
            elif isinstance(node, ast.Try):
                patterns.append({
                    "type": "error_handling",
                    "line": node.lineno,
                    "description": "Error handling pattern"
                })

        return patterns

    def _analyze_imports(self, tree: ast.AST) -> List[Dict]:
        """Analyze imports"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        "type": "import",
                        "name": name.name,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                imports.append({
                    "type": "import_from",
                    "module": node.module,
                    "names": [name.name for name in node.names],
                    "line": node.lineno
                })
        return imports

    def _find_potential_issues(self, tree: ast.AST) -> List[Dict]:
        """Find potential code issues"""
        issues = []

        for node in ast.walk(tree):
            # Check for mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "type": "mutable_default",
                            "line": node.lineno,
                            "message": "Mutable default argument used"
                        })

            # Check for potentially dangerous operations
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        issues.append({
                            "type": "dangerous_call",
                            "line": node.lineno,
                            "message": f"Potentially dangerous {node.func.id}() call"
                        })

        return issues