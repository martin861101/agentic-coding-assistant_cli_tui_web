"""
Implementation Plan System
==========================

Manages subtask-based implementation plans with phases, verification,
and status tracking. Bridges Auto-Claude's implementation_plan system.
"""

import json
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

# Try to import from backend
try:
    BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
    if BACKEND_PATH.exists() and str(BACKEND_PATH) not in sys.path:
        sys.path.insert(0, str(BACKEND_PATH))
    
    from implementation_plan import (
        WorkflowType as _WorkflowType,
        PhaseType as _PhaseType,
        SubtaskStatus as _SubtaskStatus,
        VerificationType as _VerificationType,
        Verification as _Verification,
        Subtask as _Subtask,
        Phase as _Phase,
        ImplementationPlan as _ImplementationPlan,
        create_feature_plan,
        create_investigation_plan,
        create_refactor_plan,
    )
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False


class WorkflowType(str, Enum):
    """Types of implementation workflows."""
    FEATURE = "feature"          # Standard multi-service feature
    REFACTOR = "refactor"        # Migration/refactor work
    INVESTIGATION = "investigation"  # Bug hunting
    MIGRATION = "migration"      # Data migration
    SIMPLE = "simple"            # Single-service enhancement


class PhaseType(str, Enum):
    """Types of implementation phases."""
    SETUP = "setup"
    BACKEND = "backend"
    FRONTEND = "frontend"
    INTEGRATION = "integration"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    INVESTIGATE = "investigate"
    HYPOTHESIZE = "hypothesize"
    FIX = "fix"
    ADD = "add"
    MIGRATE = "migrate"
    REMOVE = "remove"


class SubtaskStatus(str, Enum):
    """Status of a subtask."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class VerificationType(str, Enum):
    """Types of verification checks."""
    UNIT_TEST = "unit_test"
    INTEGRATION_TEST = "integration_test"
    MANUAL_CHECK = "manual_check"
    BUILD_SUCCESS = "build_success"
    LINT_PASS = "lint_pass"


@dataclass
class Verification:
    """A verification check for a subtask."""
    type: VerificationType
    description: str
    command: Optional[str] = None
    expected_output: Optional[str] = None
    passed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
            "description": self.description,
            "command": self.command,
            "expected_output": self.expected_output,
            "passed": self.passed,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Verification":
        return cls(
            type=VerificationType(data.get("type", "manual_check")),
            description=data.get("description", ""),
            command=data.get("command"),
            expected_output=data.get("expected_output"),
            passed=data.get("passed", False),
        )


@dataclass
class Subtask:
    """A single unit of work in the implementation plan."""
    id: str
    description: str
    status: SubtaskStatus = SubtaskStatus.PENDING
    files_to_modify: List[str] = field(default_factory=list)
    files_to_create: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    verifications: List[Verification] = field(default_factory=list)
    notes: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    attempt_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "files_to_modify": self.files_to_modify,
            "files_to_create": self.files_to_create,
            "dependencies": self.dependencies,
            "verifications": [v.to_dict() for v in self.verifications],
            "notes": self.notes,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "attempt_count": self.attempt_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subtask":
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            status=SubtaskStatus(data.get("status", "pending")),
            files_to_modify=data.get("files_to_modify", []),
            files_to_create=data.get("files_to_create", []),
            dependencies=data.get("dependencies", []),
            verifications=[Verification.from_dict(v) for v in data.get("verifications", [])],
            notes=data.get("notes", ""),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            attempt_count=data.get("attempt_count", 0),
        )
    
    def start(self):
        """Mark subtask as started."""
        self.status = SubtaskStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()
        self.attempt_count += 1
    
    def complete(self):
        """Mark subtask as completed."""
        self.status = SubtaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
    
    def fail(self, reason: str = ""):
        """Mark subtask as failed."""
        self.status = SubtaskStatus.FAILED
        if reason:
            self.notes = reason


@dataclass
class Phase:
    """A group of related subtasks."""
    id: str
    name: str
    phase_type: PhaseType = PhaseType.BACKEND
    subtasks: List[Subtask] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "phase": self.id,  # Backwards compatibility
            "name": self.name,
            "phase_type": self.phase_type.value if isinstance(self.phase_type, Enum) else self.phase_type,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "dependencies": self.dependencies,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Phase":
        phase_id = data.get("id") or data.get("phase", "")
        return cls(
            id=phase_id,
            name=data.get("name", phase_id),
            phase_type=PhaseType(data.get("phase_type", "backend")) if data.get("phase_type") else PhaseType.BACKEND,
            subtasks=[Subtask.from_dict(s) for s in data.get("subtasks", [])],
            dependencies=data.get("dependencies", []),
        )
    
    @property
    def completed_count(self) -> int:
        return sum(1 for s in self.subtasks if s.status == SubtaskStatus.COMPLETED)
    
    @property
    def total_count(self) -> int:
        return len(self.subtasks)
    
    @property
    def is_complete(self) -> bool:
        return all(s.status == SubtaskStatus.COMPLETED for s in self.subtasks)


@dataclass
class ImplementationPlan:
    """Complete implementation plan for a feature."""
    feature: str
    workflow_type: WorkflowType
    phases: List[Phase] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    qa_status: str = "pending"
    qa_iterations: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature": self.feature,
            "workflow_type": self.workflow_type.value if isinstance(self.workflow_type, Enum) else self.workflow_type,
            "phases": [p.to_dict() for p in self.phases],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "qa_status": self.qa_status,
            "qa_iterations": self.qa_iterations,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImplementationPlan":
        return cls(
            feature=data.get("feature", "Unknown Feature"),
            workflow_type=WorkflowType(data.get("workflow_type", "feature")),
            phases=[Phase.from_dict(p) for p in data.get("phases", [])],
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            qa_status=data.get("qa_status", "pending"),
            qa_iterations=data.get("qa_iterations", 0),
        )
    
    @property
    def all_subtasks(self) -> List[Subtask]:
        """Get all subtasks across all phases."""
        return [s for p in self.phases for s in p.subtasks]
    
    @property
    def completed_count(self) -> int:
        return sum(1 for s in self.all_subtasks if s.status == SubtaskStatus.COMPLETED)
    
    @property
    def total_count(self) -> int:
        return len(self.all_subtasks)
    
    @property
    def progress_percent(self) -> float:
        if self.total_count == 0:
            return 0.0
        return (self.completed_count / self.total_count) * 100
    
    @property
    def is_complete(self) -> bool:
        return all(p.is_complete for p in self.phases)
    
    def get_next_subtask(self) -> Optional[Subtask]:
        """Get the next pending subtask to work on."""
        for phase in self.phases:
            for subtask in phase.subtasks:
                if subtask.status == SubtaskStatus.PENDING:
                    # Check dependencies
                    deps_satisfied = all(
                        self.get_subtask(dep) and self.get_subtask(dep).status == SubtaskStatus.COMPLETED
                        for dep in subtask.dependencies
                    )
                    if deps_satisfied:
                        return subtask
        return None
    
    def get_subtask(self, subtask_id: str) -> Optional[Subtask]:
        """Find a subtask by ID."""
        for phase in self.phases:
            for subtask in phase.subtasks:
                if subtask.id == subtask_id:
                    return subtask
        return None
    
    def get_phase_for_subtask(self, subtask_id: str) -> Optional[Phase]:
        """Find the phase containing a subtask."""
        for phase in self.phases:
            for subtask in phase.subtasks:
                if subtask.id == subtask_id:
                    return phase
        return None
    
    def update_subtask_status(self, subtask_id: str, status: SubtaskStatus) -> bool:
        """Update a subtask's status."""
        subtask = self.get_subtask(subtask_id)
        if subtask:
            subtask.status = status
            if status == SubtaskStatus.IN_PROGRESS:
                subtask.start()
            elif status == SubtaskStatus.COMPLETED:
                subtask.complete()
            self.updated_at = datetime.now().isoformat()
            return True
        return False


class ImplementationPlanManager:
    """
    Manages implementation plans for specs.
    
    Handles loading, saving, and updating implementation plans.
    """
    
    def __init__(self, spec_dir: Path):
        """
        Initialize the plan manager.
        
        Args:
            spec_dir: Directory containing the spec
        """
        self.spec_dir = Path(spec_dir)
        self.plan_file = self.spec_dir / "implementation_plan.json"
        self._plan: Optional[ImplementationPlan] = None
    
    def load(self) -> Optional[ImplementationPlan]:
        """Load the implementation plan from disk."""
        if not self.plan_file.exists():
            return None
        
        try:
            data = json.loads(self.plan_file.read_text())
            self._plan = ImplementationPlan.from_dict(data)
            return self._plan
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading implementation plan: {e}")
            return None
    
    def save(self, plan: Optional[ImplementationPlan] = None) -> bool:
        """Save the implementation plan to disk."""
        plan = plan or self._plan
        if not plan:
            return False
        
        try:
            self.plan_file.parent.mkdir(parents=True, exist_ok=True)
            self.plan_file.write_text(
                json.dumps(plan.to_dict(), indent=2)
            )
            self._plan = plan
            return True
        except Exception as e:
            print(f"Error saving implementation plan: {e}")
            return False
    
    @property
    def plan(self) -> Optional[ImplementationPlan]:
        """Get the current plan, loading if needed."""
        if self._plan is None:
            self.load()
        return self._plan
    
    def create_plan(
        self,
        feature: str,
        workflow_type: WorkflowType = WorkflowType.FEATURE,
        phases: Optional[List[Dict[str, Any]]] = None,
    ) -> ImplementationPlan:
        """
        Create a new implementation plan.
        
        Args:
            feature: Name of the feature
            workflow_type: Type of workflow
            phases: Optional list of phase definitions
            
        Returns:
            New ImplementationPlan
        """
        plan = ImplementationPlan(
            feature=feature,
            workflow_type=workflow_type,
        )
        
        if phases:
            for phase_data in phases:
                plan.phases.append(Phase.from_dict(phase_data))
        
        self._plan = plan
        return plan
    
    def get_progress(self) -> Dict[str, Any]:
        """Get progress summary."""
        plan = self.plan
        if not plan:
            return {"error": "No plan loaded"}
        
        return {
            "feature": plan.feature,
            "workflow_type": plan.workflow_type.value,
            "completed": plan.completed_count,
            "total": plan.total_count,
            "progress_percent": plan.progress_percent,
            "is_complete": plan.is_complete,
            "qa_status": plan.qa_status,
            "phases": [
                {
                    "name": p.name,
                    "completed": p.completed_count,
                    "total": p.total_count,
                    "is_complete": p.is_complete,
                }
                for p in plan.phases
            ],
        }
    
    def get_next_subtask(self) -> Optional[Dict[str, Any]]:
        """Get the next subtask to work on."""
        plan = self.plan
        if not plan:
            return None
        
        subtask = plan.get_next_subtask()
        if not subtask:
            return None
        
        phase = plan.get_phase_for_subtask(subtask.id)
        return {
            "id": subtask.id,
            "description": subtask.description,
            "phase_name": phase.name if phase else None,
            "files_to_modify": subtask.files_to_modify,
            "files_to_create": subtask.files_to_create,
            "dependencies": subtask.dependencies,
            "attempt_count": subtask.attempt_count,
        }
    
    def update_subtask_status(
        self,
        subtask_id: str,
        status: SubtaskStatus,
        notes: str = "",
    ) -> bool:
        """
        Update a subtask's status.
        
        Args:
            subtask_id: ID of the subtask
            status: New status
            notes: Optional notes
            
        Returns:
            True if updated successfully
        """
        plan = self.plan
        if not plan:
            return False
        
        success = plan.update_subtask_status(subtask_id, status)
        if success and notes:
            subtask = plan.get_subtask(subtask_id)
            if subtask:
                subtask.notes = notes
        
        if success:
            self.save()
        
        return success


def create_implementation_plan(
    feature: str,
    workflow_type: str = "feature",
    phases: Optional[List[Dict[str, Any]]] = None,
    spec_dir: Optional[Path] = None,
) -> ImplementationPlan:
    """
    Create a new implementation plan.
    
    Args:
        feature: Name of the feature
        workflow_type: Type of workflow (feature, refactor, investigation, etc.)
        phases: Optional list of phase definitions
        spec_dir: Optional spec directory to save to
        
    Returns:
        New ImplementationPlan
    """
    plan = ImplementationPlan(
        feature=feature,
        workflow_type=WorkflowType(workflow_type),
    )
    
    if phases:
        for phase_data in phases:
            plan.phases.append(Phase.from_dict(phase_data))
    
    if spec_dir:
        manager = ImplementationPlanManager(spec_dir)
        manager.save(plan)
    
    return plan
