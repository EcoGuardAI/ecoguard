"""Tests for the issue representation classes."""

from datetime import datetime

from ecoguard_ai.core.issue import Category, Fix, Impact, Issue, Severity


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.DEBUG.value == "debug"
        assert Severity.INFO.value == "info"
        assert Severity.WARNING.value == "warning"
        assert Severity.ERROR.value == "error"
        assert Severity.CRITICAL.value == "critical"

    def test_severity_comparison(self):
        """Test severity comparison operators."""
        assert Severity.DEBUG < Severity.INFO
        assert Severity.INFO < Severity.WARNING
        assert Severity.WARNING < Severity.ERROR
        assert Severity.ERROR < Severity.CRITICAL

        assert Severity.CRITICAL > Severity.ERROR
        assert Severity.ERROR > Severity.WARNING


class TestCategory:
    """Tests for Category enum."""

    def test_category_values(self):
        """Test category enum values."""
        assert Category.QUALITY.value == "quality"
        assert Category.SECURITY.value == "security"
        assert Category.GREEN.value == "green"
        assert Category.AI_CODE.value == "ai_code"
        assert Category.SYNTAX.value == "syntax"
        assert Category.SYSTEM.value == "system"


class TestImpact:
    """Tests for Impact dataclass."""

    def test_default_impact(self):
        """Test default impact values."""
        impact = Impact()

        assert impact.performance == 0.0
        assert impact.security_risk == 0.0
        assert impact.carbon_impact == 0.0
        assert impact.maintainability == 0.0
        assert impact.cost_impact == 0.0

    def test_custom_impact(self):
        """Test custom impact values."""
        impact = Impact(
            performance=0.5,
            security_risk=0.8,
            carbon_impact=10.5,
            maintainability=0.3,
            cost_impact=25.0,
        )

        assert impact.performance == 0.5
        assert impact.security_risk == 0.8
        assert impact.carbon_impact == 10.5
        assert impact.maintainability == 0.3
        assert impact.cost_impact == 25.0


class TestFix:
    """Tests for Fix dataclass."""

    def test_basic_fix(self):
        """Test basic fix creation."""
        fix = Fix(description="Replace with list comprehension")

        assert fix.description == "Replace with list comprehension"
        assert fix.replacement_code is None
        assert fix.can_auto_fix is False
        assert fix.confidence == 0.0
        assert fix.instructions is None

    def test_automated_fix(self):
        """Test automated fix creation."""
        fix = Fix(
            description="Use list comprehension",
            replacement_code="result = [x for x in items]",
            can_auto_fix=True,
            confidence=0.9,
            instructions="This is a safe automated fix",
        )

        assert fix.description == "Use list comprehension"
        assert fix.replacement_code == "result = [x for x in items]"
        assert fix.can_auto_fix is True
        assert fix.confidence == 0.9
        assert fix.instructions == "This is a safe automated fix"


class TestIssue:
    """Tests for Issue dataclass."""

    def test_basic_issue(self):
        """Test basic issue creation."""
        issue = Issue(
            rule_id="test_rule",
            category="quality",
            severity="warning",
            message="Test issue message",
            file_path="/path/to/file.py",
            line=10,
            column=5,
        )

        assert issue.rule_id == "test_rule"
        assert issue.category == Category.QUALITY
        assert issue.severity == Severity.WARNING
        assert issue.message == "Test issue message"
        assert issue.file_path == "/path/to/file.py"
        assert issue.line == 10
        assert issue.column == 5
        assert issue.end_line is None
        assert issue.end_column is None
        assert isinstance(issue.created_at, datetime)

    def test_issue_with_enums(self):
        """Test issue creation with enum values."""
        issue = Issue(
            rule_id="test_rule",
            category=Category.SECURITY,
            severity=Severity.ERROR,
            message="Security issue",
            file_path="/path/to/file.py",
            line=5,
        )

        assert issue.category == Category.SECURITY
        assert issue.severity == Severity.ERROR

    def test_issue_severity_score(self):
        """Test severity score property."""
        debug_issue = Issue(
            rule_id="test",
            category="quality",
            severity="debug",
            message="Debug",
            file_path="test.py",
            line=1,
        )
        warning_issue = Issue(
            rule_id="test",
            category="quality",
            severity="warning",
            message="Warning",
            file_path="test.py",
            line=1,
        )
        critical_issue = Issue(
            rule_id="test",
            category="quality",
            severity="critical",
            message="Critical",
            file_path="test.py",
            line=1,
        )

        assert debug_issue.severity_score == 1
        assert warning_issue.severity_score == 3
        assert critical_issue.severity_score == 5

    def test_issue_to_dict(self):
        """Test issue to dictionary conversion."""
        impact = Impact(performance=0.5)
        fix = Fix(description="Test fix")

        issue = Issue(
            rule_id="test_rule",
            category="green",
            severity="info",
            message="Test message",
            file_path="test.py",
            line=1,
            column=0,
            impact=impact,
            suggested_fix=fix,
            tags=["test", "example"],
        )

        issue_dict = issue.to_dict()

        assert issue_dict["rule_id"] == "test_rule"
        assert issue_dict["category"] == "green"
        assert issue_dict["severity"] == "info"
        assert issue_dict["message"] == "Test message"
        assert issue_dict["file_path"] == "test.py"
        assert issue_dict["line"] == 1
        assert issue_dict["column"] == 0
        assert issue_dict["impact"]["performance"] == 0.5
        assert issue_dict["suggested_fix"]["description"] == "Test fix"
        assert issue_dict["tags"] == ["test", "example"]

    def test_issue_from_dict(self):
        """Test issue creation from dictionary."""
        issue_data = {
            "rule_id": "test_rule",
            "category": "security",
            "severity": "error",
            "message": "Test message",
            "file_path": "test.py",
            "line": 5,
            "column": 10,
            "tags": ["security", "test"],
            "impact": {"security_risk": 0.8},
            "suggested_fix": {"description": "Fix this issue"},
        }

        issue = Issue.from_dict(issue_data)

        assert issue.rule_id == "test_rule"
        assert issue.category == Category.SECURITY
        assert issue.severity == Severity.ERROR
        assert issue.message == "Test message"
        assert issue.line == 5
        assert issue.column == 10
        assert issue.tags == ["security", "test"]
        assert issue.impact.security_risk == 0.8
        assert issue.suggested_fix.description == "Fix this issue"

    def test_issue_str_representation(self):
        """Test string representation of issue."""
        issue = Issue(
            rule_id="test_rule",
            category="quality",
            severity="warning",
            message="Test message",
            file_path="test.py",
            line=10,
            column=5,
        )

        expected = "test.py:10:5: warning: Test message [test_rule]"
        assert str(issue) == expected
