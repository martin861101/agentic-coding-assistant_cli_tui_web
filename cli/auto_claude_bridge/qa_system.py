"""
QA Validation System
====================

Bridges the Auto-Claude QA validation loop with ARIA.
Provides automated review and fix cycles.
"""

import json
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

# Try to import from backend
try:
    BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
    if BACKEND_PATH.exists() and str(BACKEND_PATH) not in sys.path:
        sys.path.insert(0, str(BACKEND_PATH))
    
    from qa import (
        run_qa_validation_loop as _run_qa_loop,
        should_run_qa,
        is_qa_approved,
        is_qa_rejected,
        get_qa_signoff_status,
        get_qa_iteration_count,
        has_recurring_issues,
        escalate_to_human,
        MAX_QA_ITERATIONS,
    )
    QA_BACKEND_AVAILABLE = True
except ImportError:
    QA_BACKEND_AVAILABLE = False
    MAX_QA_ITERATIONS = 5


class QAStatus(str, Enum):
    """Status of QA validation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_FIXES = "needs_fixes"
    ESCALATED = "escalated"


class QAIssue:
    """A QA issue found during validation."""
    
    def __init__(
        self,
        id: str,
        description: str,
        severity: str = "medium",
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None,
    ):
        self.id = id
        self.description = description
        self.severity = severity  # low, medium, high, critical
        self.file_path = file_path
        self.line_number = line_number
        self.suggestion = suggestion
        self.fixed = False
        self.fix_attempt_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "severity": self.severity,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "suggestion": self.suggestion,
            "fixed": self.fixed,
            "fix_attempt_count": self.fix_attempt_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QAIssue":
        issue = cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            severity=data.get("severity", "medium"),
            file_path=data.get("file_path"),
            line_number=data.get("line_number"),
            suggestion=data.get("suggestion"),
        )
        issue.fixed = data.get("fixed", False)
        issue.fix_attempt_count = data.get("fix_attempt_count", 0)
        return issue


class QAReport:
    """A QA validation report."""
    
    def __init__(self, iteration: int = 1):
        self.iteration = iteration
        self.status = QAStatus.PENDING
        self.issues: List[QAIssue] = []
        self.tests_passed: List[str] = []
        self.tests_failed: List[str] = []
        self.summary = ""
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "iteration": self.iteration,
            "status": self.status.value,
            "issues": [i.to_dict() for i in self.issues],
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "summary": self.summary,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QAReport":
        report = cls(iteration=data.get("iteration", 1))
        report.status = QAStatus(data.get("status", "pending"))
        report.issues = [QAIssue.from_dict(i) for i in data.get("issues", [])]
        report.tests_passed = data.get("tests_passed", [])
        report.tests_failed = data.get("tests_failed", [])
        report.summary = data.get("summary", "")
        report.created_at = data.get("created_at", datetime.now().isoformat())
        return report
    
    @property
    def is_approved(self) -> bool:
        return self.status == QAStatus.APPROVED
    
    @property
    def needs_fixes(self) -> bool:
        return bool(self.issues) and not all(i.fixed for i in self.issues)
    
    @property
    def open_issues_count(self) -> int:
        return sum(1 for i in self.issues if not i.fixed)


class QAValidator:
    """
    Manages QA validation for a spec.
    
    Provides:
    - Automated QA review sessions
    - Issue tracking and fix cycles
    - Recurring issue detection
    - Human escalation
    """
    
    def __init__(
        self,
        spec_dir: Path,
        project_dir: Optional[Path] = None,
        max_iterations: int = MAX_QA_ITERATIONS,
    ):
        """
        Initialize the QA validator.
        
        Args:
            spec_dir: Directory containing the spec
            project_dir: Root project directory
            max_iterations: Maximum QA iterations before escalation
        """
        self.spec_dir = Path(spec_dir)
        self.project_dir = Path(project_dir) if project_dir else self.spec_dir.parent.parent.parent
        self.max_iterations = max_iterations
        self.qa_dir = self.spec_dir / "qa"
        self.qa_dir.mkdir(exist_ok=True)
        
        self._reports: List[QAReport] = []
        self._load_reports()
    
    def _load_reports(self):
        """Load existing QA reports from disk."""
        reports_file = self.qa_dir / "reports.json"
        if reports_file.exists():
            try:
                data = json.loads(reports_file.read_text())
                self._reports = [QAReport.from_dict(r) for r in data]
            except json.JSONDecodeError:
                self._reports = []
    
    def _save_reports(self):
        """Save QA reports to disk."""
        reports_file = self.qa_dir / "reports.json"
        reports_file.write_text(
            json.dumps([r.to_dict() for r in self._reports], indent=2)
        )
    
    @property
    def current_iteration(self) -> int:
        """Get the current QA iteration number."""
        return len(self._reports) + 1
    
    @property
    def latest_report(self) -> Optional[QAReport]:
        """Get the most recent QA report."""
        return self._reports[-1] if self._reports else None
    
    @property
    def is_approved(self) -> bool:
        """Check if QA has been approved."""
        return self.latest_report is not None and self.latest_report.is_approved
    
    @property
    def should_escalate(self) -> bool:
        """Check if we should escalate to human review."""
        if len(self._reports) >= self.max_iterations:
            return True
        
        # Check for recurring issues
        if len(self._reports) >= 2:
            recent_issues = set()
            for report in self._reports[-2:]:
                for issue in report.issues:
                    recent_issues.add(issue.description[:50])
            
            # If same issues keep appearing, escalate
            if len(recent_issues) > 0:
                overlap = 0
                for report in self._reports[:-2]:
                    for issue in report.issues:
                        if issue.description[:50] in recent_issues:
                            overlap += 1
                if overlap >= 2:
                    return True
        
        return False
    
    def create_report(self) -> QAReport:
        """Create a new QA report for this iteration."""
        report = QAReport(iteration=self.current_iteration)
        return report
    
    def submit_report(self, report: QAReport):
        """Submit a completed QA report."""
        self._reports.append(report)
        self._save_reports()
        
        # Update implementation plan QA status
        plan_file = self.spec_dir / "implementation_plan.json"
        if plan_file.exists():
            try:
                plan = json.loads(plan_file.read_text())
                plan["qa_status"] = report.status.value
                plan["qa_iterations"] = len(self._reports)
                plan_file.write_text(json.dumps(plan, indent=2))
            except (json.JSONDecodeError, KeyError):
                pass
    
    def add_issue(
        self,
        report: QAReport,
        description: str,
        severity: str = "medium",
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None,
    ) -> QAIssue:
        """Add an issue to a QA report."""
        issue_id = f"QA-{report.iteration}-{len(report.issues) + 1}"
        issue = QAIssue(
            id=issue_id,
            description=description,
            severity=severity,
            file_path=file_path,
            line_number=line_number,
            suggestion=suggestion,
        )
        report.issues.append(issue)
        return issue
    
    def mark_issue_fixed(self, issue_id: str) -> bool:
        """Mark an issue as fixed."""
        for report in reversed(self._reports):
            for issue in report.issues:
                if issue.id == issue_id:
                    issue.fixed = True
                    self._save_reports()
                    return True
        return False
    
    def get_open_issues(self) -> List[QAIssue]:
        """Get all open (unfixed) issues."""
        open_issues = []
        for report in self._reports:
            for issue in report.issues:
                if not issue.fixed:
                    open_issues.append(issue)
        return open_issues
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of QA status."""
        return {
            "iterations": len(self._reports),
            "max_iterations": self.max_iterations,
            "status": self.latest_report.status.value if self.latest_report else "pending",
            "is_approved": self.is_approved,
            "should_escalate": self.should_escalate,
            "open_issues_count": len(self.get_open_issues()),
            "total_issues_found": sum(len(r.issues) for r in self._reports),
            "tests_passed": self.latest_report.tests_passed if self.latest_report else [],
            "tests_failed": self.latest_report.tests_failed if self.latest_report else [],
        }
    
    def generate_qa_prompt(self, focus_areas: Optional[List[str]] = None) -> str:
        """Generate a prompt for QA review."""
        prompt_parts = [
            "# QA Validation Review",
            "",
            f"This is QA iteration {self.current_iteration} of {self.max_iterations}.",
            "",
            "## Your Task",
            "Review the implementation against the spec requirements.",
            "Run any automated tests and verify the feature works correctly.",
            "",
        ]
        
        if focus_areas:
            prompt_parts.extend([
                "## Focus Areas",
                "Pay special attention to:",
            ])
            for area in focus_areas:
                prompt_parts.append(f"- {area}")
            prompt_parts.append("")
        
        open_issues = self.get_open_issues()
        if open_issues:
            prompt_parts.extend([
                "## Outstanding Issues",
                "The following issues from previous reviews need verification:",
            ])
            for issue in open_issues:
                prompt_parts.append(f"- [{issue.id}] {issue.description}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "## Required Actions",
            "1. Run the test suite and report results",
            "2. Verify acceptance criteria are met",
            "3. Check for edge cases and error handling",
            "4. If issues found, document them clearly",
            "5. Update qa_status to 'approved' or 'needs_fixes'",
        ])
        
        return "\n".join(prompt_parts)


async def run_qa_validation(
    spec_dir: Path,
    project_dir: Optional[Path] = None,
    model: str = "claude-sonnet-4-20250514",
    on_iteration: Optional[Callable[[QAReport], None]] = None,
) -> Dict[str, Any]:
    """
    Run the full QA validation loop.
    
    Args:
        spec_dir: Directory containing the spec
        project_dir: Root project directory
        model: Model to use for QA sessions
        on_iteration: Optional callback after each iteration
        
    Returns:
        Final QA status dict
    """
    validator = QAValidator(spec_dir, project_dir)
    
    # If backend available, use its loop
    if QA_BACKEND_AVAILABLE:
        try:
            await _run_qa_loop(
                spec_dir=spec_dir,
                project_dir=project_dir or spec_dir.parent.parent.parent,
                model=model,
            )
            # Reload reports after backend loop
            validator._load_reports()
            return validator.get_summary()
        except Exception as e:
            print(f"Backend QA loop failed: {e}, using fallback")
    
    # Simplified fallback - just return current status
    return validator.get_summary()
