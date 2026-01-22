"""
Runners Module
==============

High-level runners for autonomous builds, spec generation, 
roadmap discovery, and ideation.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

# Try to import from backend
try:
    BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
    if BACKEND_PATH.exists() and str(BACKEND_PATH) not in sys.path:
        sys.path.insert(0, str(BACKEND_PATH))
    
    from agents import run_autonomous_agent as _run_autonomous_agent
    RUNNERS_BACKEND_AVAILABLE = True
except ImportError:
    RUNNERS_BACKEND_AVAILABLE = False


async def run_autonomous_build(
    project_dir: Path,
    spec_dir: Path,
    model: str = "claude-sonnet-4-20250514",
    max_iterations: Optional[int] = None,
    verbose: bool = False,
    on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Run the full autonomous build loop.
    
    This is the main entry point for autonomous feature building.
    It will:
    1. Run the planner agent to create an implementation plan
    2. Execute subtasks with the coder agent
    3. Run QA validation (if enabled)
    4. Handle memory and recovery
    
    Args:
        project_dir: Root directory of the project
        spec_dir: Directory containing the spec (auto-claude/specs/XXX-name/)
        model: Claude model to use
        max_iterations: Maximum iterations (None = unlimited)
        verbose: Whether to show detailed output
        on_progress: Optional callback for progress updates
        
    Returns:
        Build result dict with status and progress
    """
    from .implementation import ImplementationPlanManager
    from .memory import GraphitiMemoryManager
    from .qa_system import QAValidator
    from .config import get_config
    
    result = {
        "status": "pending",
        "completed_subtasks": 0,
        "total_subtasks": 0,
        "iterations": 0,
        "qa_status": "pending",
        "errors": [],
    }
    
    # Use backend runner if available
    if RUNNERS_BACKEND_AVAILABLE:
        try:
            await _run_autonomous_agent(
                project_dir=project_dir,
                spec_dir=spec_dir,
                model=model,
                max_iterations=max_iterations,
                verbose=verbose,
            )
            
            # Get final status
            plan_manager = ImplementationPlanManager(spec_dir)
            progress = plan_manager.get_progress()
            result.update({
                "status": "complete" if progress.get("is_complete") else "in_progress",
                "completed_subtasks": progress.get("completed", 0),
                "total_subtasks": progress.get("total", 0),
                "qa_status": progress.get("qa_status", "pending"),
            })
            
            return result
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
            return result
    
    # Fallback: simplified build loop for when backend not available
    print("Note: Full autonomous agent not available, using simplified runner")
    
    plan_manager = ImplementationPlanManager(spec_dir)
    memory = GraphitiMemoryManager(spec_dir, project_dir)
    
    # Check if we have a plan
    plan = plan_manager.load()
    if not plan:
        result["status"] = "needs_planning"
        result["message"] = "No implementation plan found. Create a spec first."
        return result
    
    result["total_subtasks"] = plan.total_count
    result["completed_subtasks"] = plan.completed_count
    
    if plan.is_complete:
        result["status"] = "complete"
        result["qa_status"] = plan.qa_status
    else:
        result["status"] = "in_progress"
        next_subtask = plan.get_next_subtask()
        if next_subtask:
            result["next_subtask"] = {
                "id": next_subtask.id,
                "description": next_subtask.description,
            }
    
    return result


async def run_spec(
    project_dir: Path,
    spec_name: str,
    description: str,
    model: str = "claude-sonnet-4-20250514",
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run the spec creation workflow.
    
    Creates a new spec directory with:
    - spec.md: The specification document
    - implementation_plan.json: The subtask-based plan
    
    Args:
        project_dir: Root directory of the project
        spec_name: Name for the spec (e.g., "add-user-auth")
        description: Description of the feature to build
        model: Claude model to use
        output_dir: Custom output directory (default: auto-claude/specs/)
        
    Returns:
        Result dict with spec_dir path and status
    """
    from .implementation import create_implementation_plan, WorkflowType
    from datetime import datetime
    
    # Create spec directory
    specs_base = output_dir or (project_dir / "auto-claude" / "specs")
    specs_base.mkdir(parents=True, exist_ok=True)
    
    # Generate spec number
    existing_specs = list(specs_base.glob("*-*"))
    next_num = len(existing_specs) + 1
    spec_id = f"{next_num:03d}-{spec_name}"
    spec_dir = specs_base / spec_id
    spec_dir.mkdir(exist_ok=True)
    
    # Create spec.md
    spec_content = f"""# {spec_name.replace('-', ' ').title()}

## Description

{description}

## Requirements

<!-- Add specific requirements here -->

## Acceptance Criteria

- [ ] Feature works as described
- [ ] Tests pass
- [ ] Documentation updated

## Technical Notes

<!-- Add technical implementation notes -->

---
*Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    spec_file = spec_dir / "spec.md"
    spec_file.write_text(spec_content)
    
    # Create initial implementation plan (empty, to be filled by planner)
    create_implementation_plan(
        feature=spec_name.replace('-', ' ').title(),
        workflow_type="feature",
        spec_dir=spec_dir,
    )
    
    return {
        "status": "created",
        "spec_dir": str(spec_dir),
        "spec_id": spec_id,
        "spec_file": str(spec_file),
    }


async def run_roadmap(
    project_dir: Path,
    model: str = "claude-sonnet-4-20250514",
    output_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run roadmap discovery to generate a product roadmap.
    
    Analyzes the project and suggests features for development.
    
    Args:
        project_dir: Root directory of the project
        model: Claude model to use
        output_file: Where to save the roadmap
        
    Returns:
        Roadmap result with suggested features
    """
    # Try backend runner
    if RUNNERS_BACKEND_AVAILABLE:
        try:
            BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
            sys.path.insert(0, str(BACKEND_PATH))
            from runners import run_roadmap as _run_roadmap
            return await _run_roadmap(project_dir, model=model)
        except ImportError:
            pass
    
    # Fallback: return placeholder
    return {
        "status": "not_available",
        "message": "Roadmap runner requires full backend. Please run: python Auto-Claude/apps/backend/run.py --roadmap",
    }


async def run_ideation(
    project_dir: Path,
    focus_area: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514",
) -> Dict[str, Any]:
    """
    Run ideation to generate feature ideas.
    
    Analyzes the project and generates creative feature suggestions.
    
    Args:
        project_dir: Root directory of the project
        focus_area: Optional area to focus ideation on
        model: Claude model to use
        
    Returns:
        Ideation result with feature ideas
    """
    # Try backend runner
    if RUNNERS_BACKEND_AVAILABLE:
        try:
            BACKEND_PATH = Path(__file__).parent.parent / "Auto-Claude" / "apps" / "backend"
            sys.path.insert(0, str(BACKEND_PATH))
            from runners import run_ideation as _run_ideation
            return await _run_ideation(project_dir, focus_area=focus_area, model=model)
        except ImportError:
            pass
    
    # Fallback: return placeholder
    return {
        "status": "not_available",
        "message": "Ideation runner requires full backend. Please run: python Auto-Claude/apps/backend/run.py --ideation",
    }


async def run_insights(
    spec_dir: Path,
    project_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Extract insights from completed sessions.
    
    Analyzes session logs to extract patterns, discoveries, and gotchas.
    
    Args:
        spec_dir: Directory containing the spec
        project_dir: Root directory of the project
        
    Returns:
        Extracted insights
    """
    from .memory import GraphitiMemoryManager
    
    memory = GraphitiMemoryManager(spec_dir, project_dir)
    stats = memory.get_stats()
    
    return {
        "status": "success",
        "insights": stats,
    }


def list_specs(project_dir: Path) -> List[Dict[str, Any]]:
    """
    List all specs in a project.
    
    Args:
        project_dir: Root directory of the project
        
    Returns:
        List of spec info dicts
    """
    from .implementation import ImplementationPlanManager
    
    specs_dir = project_dir / "auto-claude" / "specs"
    if not specs_dir.exists():
        return []
    
    specs = []
    for spec_dir in sorted(specs_dir.iterdir()):
        if not spec_dir.is_dir():
            continue
        
        spec_info = {
            "id": spec_dir.name,
            "path": str(spec_dir),
            "has_spec": (spec_dir / "spec.md").exists(),
            "has_plan": (spec_dir / "implementation_plan.json").exists(),
        }
        
        # Get progress if plan exists
        if spec_info["has_plan"]:
            manager = ImplementationPlanManager(spec_dir)
            progress = manager.get_progress()
            spec_info.update({
                "feature": progress.get("feature", "Unknown"),
                "completed": progress.get("completed", 0),
                "total": progress.get("total", 0),
                "progress_percent": progress.get("progress_percent", 0),
                "is_complete": progress.get("is_complete", False),
                "qa_status": progress.get("qa_status", "pending"),
            })
        
        specs.append(spec_info)
    
    return specs


def get_spec_status(spec_dir: Path) -> Dict[str, Any]:
    """
    Get the current status of a spec.
    
    Args:
        spec_dir: Directory containing the spec
        
    Returns:
        Status dict with progress and next steps
    """
    from .implementation import ImplementationPlanManager
    from .memory import GraphitiMemoryManager
    from .qa_system import QAValidator
    
    result = {
        "spec_id": spec_dir.name,
        "has_spec": (spec_dir / "spec.md").exists(),
        "has_plan": (spec_dir / "implementation_plan.json").exists(),
    }
    
    if result["has_plan"]:
        manager = ImplementationPlanManager(spec_dir)
        result["progress"] = manager.get_progress()
        result["next_subtask"] = manager.get_next_subtask()
    
    # Memory stats
    memory = GraphitiMemoryManager(spec_dir)
    result["memory_stats"] = memory.get_stats()
    
    # QA status
    qa = QAValidator(spec_dir)
    result["qa_summary"] = qa.get_summary()
    
    return result
