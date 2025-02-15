from typing import Dict, List, Optional
import re


class BugClassifier:
    def __init__(self):
        self.error_patterns = {
            'syntax_error': [
                r'SyntaxError',
                r'IndentationError',
                r'Invalid syntax'
            ],
            'type_error': [
                r'TypeError',
                r'cannot concatenate',
                r'unsupported operand type',
                r'NoneType'
            ],
            'name_error': [
                r'NameError',
                r'undefined',
                r'is not defined'
            ],
            'import_error': [
                r'ImportError',
                r'ModuleNotFoundError',
                r'No module named'
            ],
            'attribute_error': [
                r'AttributeError',
                r'has no attribute',
                r'object has no attribute'
            ],
            'index_error': [
                r'IndexError',
                r'list index out of range',
                r'string index out of range'
            ],
            'key_error': [
                r'KeyError',
                r'dictionary key',
                r'missing key'
            ],
            'value_error': [
                r'ValueError',
                r'invalid literal',
                r'invalid value'
            ],
            'runtime_error': [
                r'RuntimeError',
                r'RecursionError',
                r'maximum recursion depth'
            ],
            'memory_error': [
                r'MemoryError',
                r'out of memory',
                r'memory allocation failed'
            ]
        }

        # Common patterns for specific languages
        self.language_patterns = {
            'python': {
                'undefined_variable': r'name \'(\w+)\' is not defined',
                'type_mismatch': r'cannot concatenate \'(\w+)\' and \'(\w+)\'',
                'indent_error': r'expected an indented block'
            },
            'javascript': {
                'undefined_variable': r'(\w+) is not defined',
                'type_mismatch': r'cannot read property .* of undefined',
                'syntax_error': r'Unexpected token'
            }
        }

        # Fix suggestions for common errors
        self.fix_suggestions = {
            'syntax_error': [
                "Check for missing parentheses, brackets, or quotes",
                "Verify correct indentation",
                "Look for missing colons in Python"
            ],
            'type_error': [
                "Convert variables to the correct type",
                "Check if variables are None before operations",
                "Verify the data types being used in operations"
            ],
            'name_error': [
                "Check if the variable is defined before use",
                "Verify variable scope",
                "Look for typos in variable names"
            ],
            'import_error': [
                "Verify the module is installed",
                "Check import statement syntax",
                "Confirm package name spelling"
            ]
        }

    def classify(self, error: str, context: Optional[str] = None, language: Optional[str] = None) -> Dict:
        """Classify the type of bug and provide analysis"""
        error_type = self._identify_error_type(error)
        severity = self._determine_severity(error_type, error)

        analysis = {
            "error_type": error_type,
            "severity": severity,
            "patterns": self._identify_patterns(error, language),
            "probable_causes": self._identify_causes(error, error_type, language),
            "suggested_fixes": self._suggest_fixes(error, error_type, language)
        }

        if context:
            analysis["context_analysis"] = self._analyze_context(context, error_type)

        return analysis

    def _identify_error_type(self, error: str) -> str:
        """Identify the type of error based on patterns"""
        error_lower = error.lower()

        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error, re.IGNORECASE):
                    return error_type

        return "unknown_error"

    def _determine_severity(self, error_type: str, error: str) -> str:
        """Determine the severity of the error"""
        critical_patterns = [
            r'memory',
            r'corruption',
            r'crash',
            r'deadlock',
            r'recursion'
        ]

        if any(re.search(pattern, error, re.IGNORECASE) for pattern in critical_patterns):
            return "critical"

        severity_map = {
            'syntax_error': 'low',
            'type_error': 'medium',
            'name_error': 'low',
            'import_error': 'low',
            'attribute_error': 'medium',
            'index_error': 'medium',
            'key_error': 'medium',
            'value_error': 'medium',
            'runtime_error': 'high',
            'memory_error': 'critical'
        }

        return severity_map.get(error_type, 'medium')

    def _identify_patterns(self, error: str, language: Optional[str] = None) -> List[str]:
        """Identify common error patterns"""
        patterns = []

        if language and language in self.language_patterns:
            lang_patterns = self.language_patterns[language]
            for pattern_name, pattern in lang_patterns.items():
                if re.search(pattern, error, re.IGNORECASE):
                    patterns.append(pattern_name)

        # Generic patterns
        if 'line' in error.lower():
            patterns.append('line_specific')
        if 'expected' in error.lower():
            patterns.append('expectation_mismatch')
        if 'undefined' in error.lower() or 'not defined' in error.lower():
            patterns.append('undefined_reference')

        return patterns

    def _identify_causes(self, error: str, error_type: str, language: Optional[str] = None) -> List[str]:
        """Identify probable causes of the error"""
        causes = []

        common_causes = {
            'syntax_error': [
                "Missing or extra parentheses/brackets",
                "Incorrect indentation",
                "Missing colons or semicolons"
            ],
            'type_error': [
                "Incompatible data types in operation",
                "Null/None value used in operation",
                "Wrong type conversion"
            ],
            'name_error': [
                "Variable not defined",
                "Variable used outside its scope",
                "Typo in variable name"
            ]
        }

        # Add common causes for the error type
        causes.extend(common_causes.get(error_type, []))

        # Add language-specific causes
        if language == 'python':
            if error_type == 'syntax_error':
                causes.append("Missing colon after control statement")
            elif error_type == 'indentation_error':
                causes.append("Inconsistent use of tabs and spaces")

        elif language == 'javascript':
            if error_type == 'type_error':
                causes.append("Accessing property of undefined")
            elif error_type == 'syntax_error':
                causes.append("Missing semicolon")

        return causes

    def _suggest_fixes(self, error: str, error_type: str, language: Optional[str] = None) -> List[str]:
        """Suggest fixes for the error"""
        suggestions = []

        # Add general suggestions for the error type
        if error_type in self.fix_suggestions:
            suggestions.extend(self.fix_suggestions[error_type])

        # Add language-specific suggestions
        if language == 'python':
            if error_type == 'type_error':
                suggestions.extend([
                    "Use str() for string conversion",
                    "Use int() for integer conversion",
                    "Use float() for float conversion"
                ])
        elif language == 'javascript':
            if error_type == 'type_error':
                suggestions.extend([
                    "Use typeof to check variable type",
                    "Check if variable is undefined before use",
                    "Use optional chaining (?.) for nested properties"
                ])

        return suggestions

    def _analyze_context(self, context: str, error_type: str) -> Dict:
        """Analyze the context of the error"""
        return {
            "scope": self._determine_scope(context),
            "complexity": self._assess_complexity(context),
            "related_code": self._extract_related_code(context, error_type)
        }

    def _determine_scope(self, context: str) -> str:
        """Determine the scope of the error"""
        if 'class' in context.lower():
            return 'class'
        elif 'function' in context.lower() or 'def' in context.lower():
            return 'function'
        elif 'loop' in context.lower() or 'for' in context.lower() or 'while' in context.lower():
            return 'loop'
        else:
            return 'global'

    def _assess_complexity(self, context: str) -> str:
        """Assess the complexity of the context"""
        context_lower = context.lower()
        if any(word in context_lower for word in ['nested', 'recursion', 'recursive']):
            return 'high'
        elif any(word in context_lower for word in ['loop', 'if', 'else', 'elif']):
            return 'medium'
        else:
            return 'low'

    def _extract_related_code(self, context: str, error_type: str) -> List[str]:
        """Extract related code snippets from context"""
        lines = context.split('\n')
        related_lines = []

        for i, line in enumerate(lines):
            if any(pattern in line for pattern in self.error_patterns.get(error_type, [])):
                # Include the error line and surrounding lines
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                related_lines.extend(lines[start:end])

        return related_lines