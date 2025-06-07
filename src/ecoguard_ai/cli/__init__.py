"""
Command-line interface for EcoGuard AI.

This module provides the main entry point for the EcoGuard AI command-line tool.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from ecoguard_ai.core.analyzer import AnalysisConfig, EcoGuardAnalyzer
from ecoguard_ai.core.issue import Severity
from ecoguard_ai.core.result import AnalysisResult, ProjectAnalysisResult

console = Console()


@click.group()
@click.version_option(version="0.1.2", prog_name="EcoGuard AI")
def cli() -> None:
    """
    EcoGuard AI: AI-augmented software development pipeline solution.

    A unified intelligence layer for analyzing code quality, security,
    and environmental sustainability in both human-written and AI-generated code.
    """
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "text", "table"]),
    default="table",
    help="Output format",
)
@click.option(
    "--severity",
    "-s",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    default="info",
    help="Minimum severity level to report",
)
@click.option("--no-quality", is_flag=True, help="Disable quality analysis")
@click.option("--no-security", is_flag=True, help="Disable security analysis")
@click.option("--no-green", is_flag=True, help="Disable green software analysis")
@click.option("--no-ai-code", is_flag=True, help="Disable AI code analysis")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Configuration file path",
)
def analyze(
    path: str,
    output: Optional[str],
    output_format: str,
    severity: str,
    no_quality: bool,
    no_security: bool,
    no_green: bool,
    no_ai_code: bool,
    config: Optional[str],
) -> None:
    """
    Analyze Python code for quality, security, and sustainability issues.

    PATH can be either a single Python file or a directory containing Python files.
    """
    try:
        # Create analysis configuration
        analysis_config = AnalysisConfig(
            output_format=output_format,
            output_file=output,
            min_severity=severity,
            enable_quality=not no_quality,
            enable_security=not no_security,
            enable_green=not no_green,
            enable_ai_code=not no_ai_code,
        )

        # Load config file if provided
        if config:
            # TODO: Implement config file loading in future stages
            console.print(
                f"[yellow]Config file support coming in future release: "
                f"{config}[/yellow]"
            )

        # Initialize analyzer
        analyzer = EcoGuardAnalyzer(analysis_config)

        # Analyze the path
        path_obj = Path(path)
        if path_obj.is_file():
            result = analyzer.analyze_file(path_obj)
            _display_single_result(result, output_format, output)
        else:
            results = analyzer.analyze_directory(path_obj)
            project_result = ProjectAnalysisResult(
                project_path=str(path_obj), file_results=results
            )
            _display_project_result(project_result, output_format, output)

        # Exit with error code if critical/error issues found
        if path_obj.is_file():
            exit_code = 1 if result.has_errors() else 0
        else:
            exit_code = 1 if any(r.has_errors() for r in results) else 0

        sys.exit(exit_code)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def version() -> None:
    """Show EcoGuard AI version information."""
    console.print("[green]EcoGuard AI v0.1.2[/green]")
    console.print("AI-augmented software development pipeline solution")
    console.print("https://github.com/ecoguard-ai/ecoguard-ai")


@cli.command()
def rules() -> None:
    """List all available analysis rules."""
    console.print("[blue]Available Analysis Rules[/blue]")
    console.print(
        "\n[yellow]Note:[/yellow] Rules will be implemented in upcoming stages:"
    )
    console.print("• Stage 1: Quality and Green Software rules")
    console.print("• Stage 2: Security and AI Code rules")
    console.print("• Stage 3+: Advanced rules and custom rule support")


def _display_single_result(
    result: AnalysisResult, format_type: str, output_file: Optional[str]
) -> None:
    """Display analysis result for a single file."""
    if format_type == "json":
        output_text = result.to_json()
        if output_file:
            Path(output_file).write_text(output_text)
            console.print(f"[green]Results saved to {output_file}[/green]")
        else:
            console.print(output_text)

    elif format_type == "text":
        output_lines = []
        output_lines.append(f"Analysis Results for: {result.file_path}")
        output_lines.append("=" * 60)

        if not result.issues:
            output_lines.append("No issues found! 🎉")
        else:
            output_lines.append(f"Found {result.issue_count} issues:")
            output_lines.append("")

            for issue in result.issues:
                output_lines.append(str(issue))

        output_text = "\n".join(output_lines)
        if output_file:
            Path(output_file).write_text(output_text)
            console.print(f"[green]Results saved to {output_file}[/green]")
        else:
            console.print(output_text)

    else:  # table format
        _display_table_result(result)


def _display_project_result(
    project_result: ProjectAnalysisResult,
    format_type: str,
    output_file: Optional[str],
) -> None:
    """Display analysis results for a project."""
    if format_type == "json":
        output_text = project_result.to_json()
        if output_file:
            Path(output_file).write_text(output_text)
            console.print(f"[green]Results saved to {output_file}[/green]")
        else:
            console.print(output_text)

    elif format_type == "text":
        output_lines = []
        output_lines.append(f"Project Analysis Results: {project_result.project_path}")
        output_lines.append("=" * 80)
        output_lines.append(f"Files analyzed: {project_result.total_files}")
        output_lines.append(f"Total issues: {project_result.total_issues}")
        output_lines.append("")

        # Summary by severity
        severity_summary = project_result.get_summary_by_severity()
        output_lines.append("Issues by Severity:")
        for severity, count in severity_summary.items():
            if count > 0:
                output_lines.append(f"  {severity.capitalize()}: {count}")

        output_lines.append("")

        # File-by-file results
        for file_result in project_result.file_results:
            if file_result.issues:
                output_lines.append(f"\n{file_result.file_path}:")
                for issue in file_result.issues:
                    output_lines.append(f"  {issue}")

        output_text = "\n".join(output_lines)
        if output_file:
            Path(output_file).write_text(output_text)
            console.print(f"[green]Results saved to {output_file}[/green]")
        else:
            console.print(output_text)

    else:  # table format
        _display_project_table(project_result)


def _display_table_result(result: AnalysisResult) -> None:
    """Display a single file result in table format."""
    console.print(f"\n[blue]Analysis Results for:[/blue] {result.file_path}")

    if not result.issues:
        console.print("[green]✅ No issues found![/green]")
        return

    # Summary table
    summary_table = Table(title="Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="magenta")

    summary_table.add_row("Total Issues", str(result.issue_count))
    summary_table.add_row("Critical", str(result.critical_count))
    summary_table.add_row("Error", str(result.error_count))
    summary_table.add_row("Warning", str(result.warning_count))
    summary_table.add_row("Info", str(result.info_count))
    summary_table.add_row("Green Score", f"{result.calculate_green_score():.1f}/100")
    summary_table.add_row(
        "Security Score", f"{result.calculate_security_score():.1f}/100"
    )

    console.print(summary_table)

    # Issues table
    issues_table = Table(title="Issues Found")
    issues_table.add_column("Line", style="dim")
    issues_table.add_column("Severity", style="bold")
    issues_table.add_column("Category", style="cyan")
    issues_table.add_column("Rule", style="blue")
    issues_table.add_column("Message", style="white")

    for issue in result.issues:
        # Handle Union types by converting to proper enum types
        severity = issue.severity if isinstance(issue.severity, Severity) else Severity(issue.severity)
        category = issue.category if isinstance(issue.category, Category) else Category(issue.category)
        
        severity_color = _get_severity_color(severity)
        issues_table.add_row(
            str(issue.line),
            Text(severity.value.upper(), style=severity_color),
            category.value,
            issue.rule_id,
            issue.message,
        )

    console.print(issues_table)


def _display_project_table(project_result: ProjectAnalysisResult) -> None:
    """Display project results in table format."""
    console.print(
        f"\n[blue]Project Analysis Results:[/blue] {project_result.project_path}"
    )

    # Summary table
    summary_table = Table(title="Project Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="magenta")

    summary_table.add_row("Files Analyzed", str(project_result.total_files))
    summary_table.add_row("Total Issues", str(project_result.total_issues))

    severity_summary = project_result.get_summary_by_severity()
    for severity, count in severity_summary.items():
        if count > 0:
            summary_table.add_row(severity.capitalize(), str(count))

    summary_table.add_row(
        "Overall Green Score",
        f"{project_result.calculate_overall_green_score():.1f}/100",
    )
    summary_table.add_row(
        "Overall Security Score",
        f"{project_result.calculate_overall_security_score():.1f}/100",
    )

    console.print(summary_table)

    # Files with issues table
    files_with_issues = [r for r in project_result.file_results if r.issues]
    if files_with_issues:
        files_table = Table(title="Files with Issues")
        files_table.add_column("File", style="cyan")
        files_table.add_column("Issues", style="magenta")
        files_table.add_column("Critical", style="red")
        files_table.add_column("Error", style="red")
        files_table.add_column("Warning", style="yellow")
        files_table.add_column("Info", style="blue")

        for file_result in files_with_issues:
            files_table.add_row(
                Path(file_result.file_path).name,
                str(file_result.issue_count),
                str(file_result.critical_count),
                str(file_result.error_count),
                str(file_result.warning_count),
                str(file_result.info_count),
            )

        console.print(files_table)
    else:
        console.print("[green]✅ No issues found in any files![/green]")


def _get_severity_color(severity: Severity) -> str:
    """Get color for severity level."""
    severity_colors = {
        Severity.DEBUG: "dim",
        Severity.INFO: "blue",
        Severity.WARNING: "yellow",
        Severity.ERROR: "red",
        Severity.CRITICAL: "red bold",
    }
    return severity_colors.get(severity, "white")


def main() -> None:
    """Main entry point for the CLI."""
    cli()  # type: ignore


if __name__ == "__main__":
    main()
