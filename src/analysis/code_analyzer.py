from typing import Dict, Optional
import ast
import re


class CodeAnalyzer:
    def analyze(self, code: str, language: Optional[str] = None) -> Dict:
        """Analyze code for common issues and patterns"""
        try:
            if language is None:
                language = self._detect_language(code)

            if language == "python":
                return self._analyze_python(code)
            elif language == "javascript":
                return self._analyze_javascript(code)
            else:
                return self._analyze_generic(code)

        except Exception as e:
            print(f"Error in code analysis: {str(e)}")
            return {
                "language": language or "unknown",
                "issues": [],
                "complexity": "unknown",
                "error": str(e)
            }

    def _detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        # Check for Python syntax
        try:
            ast.parse(code)
            return "python"
        except:
            pass

        # Check for JavaScript syntax
        js_indicators = [
            "const ", "let ", "var ", "function ", "=>", "console.log",
            "document.", "window.", "import from", "export "
        ]
        if any(indicator in code for indicator in js_indicators):
            return "javascript"

        return "unknown"

    def _analyze_python(self, code: str) -> Dict:
        """Analyze Python code"""
        try:
            tree = ast.parse(code)

            analysis = {
                "language": "python",
                "issues": [],
                "complexity": self._calculate_complexity(tree),
                "variables": self._extract_variables(tree),
                "functions": self._analyze_functions(tree),
                "imports": self._analyze_imports(tree)
            }

            # Check for common issues
            self._check_naming_conventions(tree, analysis["issues"])
            self._check_error_handling(tree, analysis["issues"])
            self._check_code_style(code, analysis["issues"])

            return analysis

        except SyntaxError as e:
            return {
                "language": "python",
                "issues": [{
                    "type": "syntax_error",
                    "message": str(e),
                    "line": e.lineno,
                    "offset": e.offset
                }],
                "complexity": "unknown"
            }
        except Exception as e:
            return {
                "language": "python",
                "issues": [{
                    "type": "analysis_error",
                    "message": str(e)
                }],
                "complexity": "unknown"
            }

    def _analyze_javascript(self, code: str) -> Dict:
        """Analyze JavaScript code"""
        analysis = {
            "language": "javascript",
            "issues": [],
            "complexity": "medium",  # Placeholder
            "patterns": self._detect_js_patterns(code)
        }

        # Check for common JS issues
        self._check_js_best_practices(code, analysis["issues"])

        return analysis

    def _analyze_generic(self, code: str) -> Dict:
        """Generic code analysis for unknown languages"""
        return {
            "language": "unknown",
            "issues": [],
            "complexity": self._estimate_complexity(code),
            "metrics": {
                "lines": len(code.splitlines()),
                "characters": len(code),
                "words": len(re.findall(r'\w+', code))
            }
        }

    def _calculate_complexity(self, tree: ast.AST) -> str:
        """Calculate code complexity score"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef)):
                complexity += 1

        if complexity < 5:
            return "low"
        elif complexity < 10:
            return "medium"
        else:
            return "high"

    def _extract_variables(self, tree: ast.AST) -> list:
        """Extract variable names and types"""
        variables = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append({
                            "name": target.id,
                            "line": target.lineno
                        })
        return variables

    def _analyze_functions(self, tree: ast.AST) -> list:
        """Analyze function definitions"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": len(node.args.args),
                    "line": node.lineno,
                    "complexity": self._calculate_function_complexity(node)
                })
        return functions

    def _analyze_imports(self, tree: ast.AST) -> list:
        """Analyze import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}")
        return imports

    def _check_naming_conventions(self, tree: ast.AST, issues: list):
        """Check Python naming conventions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower():
                    issues.append({
                        "type": "naming_convention",
                        "message": f"Function '{node.name}' should use lowercase with underscores",
                        "line": node.lineno
                    })

    def _check_error_handling(self, tree: ast.AST, issues: list):
        """Check error handling patterns"""
        has_try = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                has_try = True
                if not node.handlers:
                    issues.append({
                        "type": "error_handling",
                        "message": "Empty try block found",
                        "line": node.lineno
                    })

        if not has_try:
            issues.append({
                "type": "suggestion",
                "message": "Consider adding error handling with try-except blocks"
            })

    def _check_code_style(self, code: str, issues: list):
        """Check code style issues"""
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            if len(line.strip()) > 100:
                issues.append({
                    "type": "style",
                    "message": "Line too long (>100 characters)",
                    "line": i
                })

    def _detect_js_patterns(self, code: str) -> list:
        """Detect JavaScript patterns"""
        patterns = []
        if "new Promise" in code:
            patterns.append("promise_usage")
        if "async" in code and "await" in code:
            patterns.append("async_await")
        if "addEventListener" in code:
            patterns.append("event_listener")
        return patterns

    def _check_js_best_practices(self, code: str, issues: list):
        """Check JavaScript best practices"""
        if "var " in code:
            issues.append({
                "type": "best_practice",
                "message": "Use 'const' or 'let' instead of 'var'"
            })

        if "===" not in code and "==" in code:
            issues.append({
                "type": "best_practice",
                "message": "Use strict equality (===) instead of =="
            })

    def _estimate_complexity(self, code: str) -> str:
        """Estimate code complexity for unknown languages"""
        lines = len(code.splitlines())
        if lines < 50:
            return "low"
        elif lines < 200:
            return "medium"
        else:
            return "high"