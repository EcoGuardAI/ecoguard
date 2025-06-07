"""Core module initialization."""

from ecoguard_ai.core.analyzer import EcoGuardAnalyzer, AnalysisConfig
from ecoguard_ai.core.issue import Issue, Severity, Category, Impact, Fix
from ecoguard_ai.core.result import AnalysisResult, ProjectAnalysisResult

__all__ = [
    "EcoGuardAnalyzer",
    "AnalysisConfig", 
    "Issue",
    "Severity",
    "Category",
    "Impact",
    "Fix",
    "AnalysisResult",
    "ProjectAnalysisResult",
]
