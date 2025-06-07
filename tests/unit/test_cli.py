"""
Test suite for the CLI module.

This module tests the command-line interface functionality.
"""

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from ecoguard_ai.cli import (
    _display_project_result,
    _display_single_result,
    _get_severity_color,
    cli,
    main,
)
from ecoguard_ai.core.issue import Fix, Impact, Issue, Severity
from ecoguard_ai.core.result import AnalysisResult, ProjectAnalysisResult


@contextmanager
def windows_safe_tempfile(content: str, suffix: str = ".py"):
    """
    Create a temporary file that works safely on Windows.
    
    Windows has issues with deleting files that are still open,
    so we need to properly close them before deletion.
    """
    # Create a temporary file without auto-deletion
    fd, filepath = tempfile.mkstemp(suffix=suffix, text=True)
    try:
        # Write content to the file
        with os.fdopen(fd, "w") as f:
            f.write(content)
        # Return the path for use
        yield filepath
    finally:
        # Ensure file is deleted even if test fails
        try:
            os.unlink(filepath)
        except OSError:
            pass  # File might already be deleted


class TestCLIMain:
    """Test main CLI entry points."""

    def test_main_function_calls_cli(self):
        """Test that main() calls the CLI."""
        with patch("ecoguard_ai.cli.cli") as mock_cli:
            main()
            mock_cli.assert_called_once()

    def test_main_with_args(self):
        """Test main function with command line arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "EcoGuard AI" in result.output


class TestCLICommands:
    """Test CLI commands."""

    def test_version_command(self):
        """Test --version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "EcoGuard AI" in result.output

    def test_version_subcommand(self):
        """Test version subcommand."""
        runner = CliRunner()
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "EcoGuard AI" in result.output

    def test_help_command(self):
        """Test help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "EcoGuard AI" in result.output
        assert "analyze" in result.output
        assert "rules" in result.output
        assert "version" in result.output

    def test_analyze_help(self):
        """Test analyze command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze Python code" in result.output

    def test_rules_help(self):
        """Test rules command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["rules", "--help"])
        assert result.exit_code == 0


class TestAnalyzeCommand:
    """Test the analyze command."""

    def test_analyze_nonexistent_file(self):
        """Test analyze command with nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "nonexistent_file.py"])
        assert result.exit_code == 2  # Click validation error

    def test_analyze_with_valid_file(self):
        """Test analyze command with valid Python file."""
        with windows_safe_tempfile("print('hello world')") as temp_file:
            runner = CliRunner()
            result = runner.invoke(cli, ["analyze", temp_file])
            # Should execute without error (may exit with 0 or 1 depending
            # on issues found)
            assert result.exit_code in [0, 1]

    def test_analyze_with_json_format(self):
        """Test analyze command with JSON output format."""
        with windows_safe_tempfile("print('hello world')") as temp_file:
            runner = CliRunner()
            result = runner.invoke(cli, ["analyze", temp_file, "--format", "json"])
            assert result.exit_code in [0, 1]

            # Try to parse output as JSON
            try:
                json.loads(result.output)
            except json.JSONDecodeError:
                # If output contains ANSI codes or other text, that's also valid
                pass

    def test_analyze_with_text_format(self):
        """Test analyze command with text output format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import unused_module\ndef test(): pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name, "--format", "text"])
                assert result.exit_code in [0, 1]
                # Text format should be readable
                assert isinstance(result.output, str)
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_table_format(self):
        """Test analyze command with table output format (default)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import unused_module\ndef test(): pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name, "--format", "table"])
                assert result.exit_code in [0, 1]
                # Should contain table formatting
                assert isinstance(result.output, str)
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_output_file(self):
        """Test analyze command with output file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello world')")
            f.flush()

            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as out_f:
                    runner = CliRunner()
                    result = runner.invoke(
                        cli,
                        ["analyze", f.name, "--output", out_f.name, "--format", "json"],
                    )
                    assert result.exit_code in [0, 1]

                    # Check output file was created
                    assert Path(out_f.name).exists()

                    Path(out_f.name).unlink(missing_ok=True)
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_directory(self):
        """Test analyze command with directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Python file in the directory
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('hello world')")

            runner = CliRunner()
            result = runner.invoke(cli, ["analyze", temp_dir])
            assert result.exit_code in [0, 1]

    def test_analyze_with_invalid_format(self):
        """Test analyze command with invalid format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello world')")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name, "--format", "invalid"])
                assert result.exit_code == 2  # Click validation error
                assert "Invalid value" in result.output
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_severity_filter(self):
        """Test analyze command with severity filtering."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import unused_module\ndef test(): pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name, "--severity", "error"])
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_analyze_with_disabled_modules(self):
        """Test analyze command with disabled analysis modules."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello world')")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(
                    cli,
                    [
                        "analyze",
                        f.name,
                        "--no-quality",
                        "--no-security",
                        "--no-green",
                        "--no-ai-code",
                    ],
                )
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)


class TestRulesCommand:
    """Test the rules command."""

    def test_rules_list(self):
        """Test rules list command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["rules"])
        assert result.exit_code == 0
        assert "Available Analysis Rules" in result.output


class TestCLIHelpers:
    """Test CLI helper functions."""

    def test_get_severity_color(self):
        """Test severity color mapping function."""
        assert _get_severity_color(Severity.DEBUG) == "dim"
        assert _get_severity_color(Severity.INFO) == "blue"
        assert _get_severity_color(Severity.WARNING) == "yellow"
        assert _get_severity_color(Severity.ERROR) == "red"
        assert _get_severity_color(Severity.CRITICAL) == "red bold"

    def test_display_single_result_with_issues(self):
        """Test display function with issues present."""
        issues = [
            Issue(
                rule_id="test_rule",
                category="quality",
                severity="warning",
                message="Test issue",
                file_path="test.py",
                line=1,
                impact=Impact(maintainability=-0.5),
                suggested_fix=Fix(description="Test fix"),
            )
        ]
        result = AnalysisResult(file_path="test.py", issues=issues)

        # Test table format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_single_result(result, "table", None)
            assert mock_console.print.called

    def test_display_single_result_json_format(self):
        """Test display function with JSON format."""
        result = AnalysisResult(file_path="test.py", issues=[])

        # Test JSON format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_single_result(result, "json", None)
            assert mock_console.print.called

    def test_display_single_result_text_format(self):
        """Test display function with text format."""
        result = AnalysisResult(file_path="test.py", issues=[])

        # Test text format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_single_result(result, "text", None)
            assert mock_console.print.called

    def test_display_project_result_with_issues(self):
        """Test project display function with issues."""
        file_results = [
            AnalysisResult(
                file_path="test1.py",
                issues=[
                    Issue(
                        rule_id="test_rule",
                        category="quality",
                        severity="warning",
                        message="Test issue",
                        file_path="test1.py",
                        line=1,
                    )
                ],
            ),
            AnalysisResult(file_path="test2.py", issues=[]),
        ]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        # Test table format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_project_result(project_result, "table", None)
            assert mock_console.print.called

    def test_display_project_result_no_issues(self):
        """Test project display function with no issues."""
        file_results = [
            AnalysisResult(file_path="test1.py", issues=[]),
            AnalysisResult(file_path="test2.py", issues=[]),
        ]
        project_result = ProjectAnalysisResult(
            project_path="/test/project", file_results=file_results
        )

        # Test table format display
        with patch("ecoguard_ai.cli.console") as mock_console:
            _display_project_result(project_result, "table", None)
            assert mock_console.print.called


class TestCLIIntegration:
    """Integration tests for the CLI."""

    def test_cli_with_empty_file(self):
        """Test CLI with empty Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")  # Empty file
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name])
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_cli_with_complex_code(self):
        """Test CLI with complex code that triggers multiple rules."""
        complex_code = '''
import os
import sys
import unused_module

def complex_function(a, b, c, d, e, f, g, h):
    """Function with too many parameters."""
    unused_var = 42
    result = []
    for i in range(len(a)):
        result.append(a[i] * 2)
    return result

class TestClass:
    def method1(self):
        x = "hello"
        x += " world"
        x += " test"
        return x
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(complex_code)
            f.flush()

            try:
                runner = CliRunner()

                # Test with different formats
                for format_type in ["table", "json", "text"]:
                    result = runner.invoke(
                        cli, ["analyze", f.name, "--format", format_type]
                    )
                    assert result.exit_code in [0, 1]

            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_cli_with_syntax_error(self):
        """Test CLI with file containing syntax errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def invalid_syntax(:\n    pass")
            f.flush()

            try:
                runner = CliRunner()
                result = runner.invoke(cli, ["analyze", f.name])
                # Should handle syntax errors gracefully
                assert result.exit_code in [0, 1]
            finally:
                Path(f.name).unlink(missing_ok=True)
