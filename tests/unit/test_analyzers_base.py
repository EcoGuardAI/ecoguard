"""
Test suite for the analyzer base classes.

This module tests the base analyzer classes and rule framework.
"""

import ast

from ecoguard_ai.analyzers.base import ASTVisitorRule, BaseAnalyzer, BaseRule
from ecoguard_ai.core.issue import Issue


class ConcreteAnalyzer(BaseAnalyzer):
    """Concrete implementation for testing."""

    def analyze(self, tree: ast.AST, source_code: str, file_path: str):
        """Simple implementation for testing."""
        issues = []
        for rule in self.rules.values():
            if rule.enabled:
                try:
                    rule_issues = rule.check(tree, source_code, file_path)
                    issues.extend(rule_issues)
                except Exception:
                    # Skip rules that fail
                    pass
        return issues


class ConcreteRule(BaseRule):
    """Concrete implementation for testing."""

    def check(self, node: ast.AST, source_code: str, file_path: str):
        """Simple implementation for testing."""
        return [
            Issue(
                rule_id=self.rule_id,
                message="Test issue",
                severity=self.severity,
                category=self.category,
                file_path=file_path,
                line=1,
            )
        ]


class ConcreteASTRule(ASTVisitorRule):
    """Concrete implementation for testing."""

    def visit_FunctionDef(self, node):
        """Test visitor method."""
        self.add_issue(f"Function found: {node.name}", node)
        self.generic_visit(node)


class TestBaseAnalyzer:
    """Test the BaseAnalyzer class."""

    def test_initialization(self):
        """Test BaseAnalyzer initialization."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        assert analyzer.name == "Test"
        assert analyzer.description == "Test analyzer"
        assert analyzer.enabled is True
        assert analyzer.rules == {}

    def test_register_rule(self):
        """Test registering a rule."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")

        analyzer.register_rule(rule)
        assert "test_rule" in analyzer.rules
        assert analyzer.rules["test_rule"] == rule

    def test_enable_disable_rule(self):
        """Test enabling and disabling rules."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")
        analyzer.register_rule(rule)

        # Test disabling
        analyzer.disable_rule("test_rule")
        assert not analyzer.rules["test_rule"].enabled

        # Test enabling
        analyzer.enable_rule("test_rule")
        assert analyzer.rules["test_rule"].enabled

    def test_analyze_with_rules(self):
        """Test analyzing with registered rules."""
        analyzer = ConcreteAnalyzer("Test", "Test analyzer")
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")
        analyzer.register_rule(rule)

        code = "def test(): pass"
        tree = ast.parse(code)
        issues = analyzer.analyze(tree, code, "test.py")

        assert len(issues) == 1
        assert issues[0].rule_id == "test_rule"


class TestBaseRule:
    """Test the BaseRule class."""

    def test_initialization(self):
        """Test BaseRule initialization."""
        rule = ConcreteRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test description",
            category="quality",
            severity="warning",
        )

        assert rule.rule_id == "test_rule"
        assert rule.name == "Test Rule"
        assert rule.description == "Test description"
        assert rule.category == "quality"
        assert rule.severity == "warning"
        assert rule.enabled is True

    def test_create_issue(self):
        """Test creating an issue."""
        rule = ConcreteRule("test_rule", "Test Rule", "Test description", "quality")

        node = ast.parse("x = 1").body[0]
        issue = rule.create_issue("Test message", node, "test.py")

        assert issue.rule_id == "test_rule"
        assert issue.message == "Test message"
        assert issue.file_path == "test.py"


class TestASTVisitorRule:
    """Test the ASTVisitorRule class."""

    def test_initialization(self):
        """Test ASTVisitorRule initialization."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        assert rule.rule_id == "ast_rule"
        assert rule.issues == []
        assert rule.current_source_code == ""
        assert rule.current_file_path == ""

    def test_check_with_visitor(self):
        """Test checking code with visitor pattern."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        code = """
def test_function():
    pass

def another_function():
    pass
"""
        tree = ast.parse(code)
        issues = rule.check(tree, code, "test.py")

        # Should find two functions
        assert len(issues) == 2
        assert all("Function found:" in issue.message for issue in issues)

    def test_reset_and_finalize(self):
        """Test reset and finalize methods."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        rule.reset("test.py", "code")
        assert rule.current_file_path == "test.py"
        assert rule.current_source_code == "code"
        assert rule.issues == []

        # Add an issue and reset
        node = ast.parse("x = 1").body[0]
        rule.add_issue("Test", node)
        assert len(rule.issues) == 1

        rule.reset("test2.py", "code2")
        assert rule.issues == []

    def test_add_issue(self):
        """Test adding issues."""
        rule = ConcreteASTRule(
            rule_id="ast_rule",
            name="AST Rule",
            description="AST test rule",
            category="quality",
        )

        rule.reset("test.py", "x = 1")
        node = ast.parse("x = 1").body[0]

        rule.add_issue("Test issue", node)
        assert len(rule.issues) == 1
        assert rule.issues[0].message == "Test issue"
        assert rule.issues[0].file_path == "test.py"
