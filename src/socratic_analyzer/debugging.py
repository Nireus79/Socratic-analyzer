"""Workflow debugging and tracing tools."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DebugEvent:
    """Single debug event."""

    event_id: str
    timestamp: float
    event_type: str  # step_enter, step_exit, condition, state_change, error
    workflow_id: str
    step_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class WorkflowDebugTrace:
    """Complete debug trace for a workflow."""

    workflow_id: str
    workflow_name: str
    status: str = "running"  # running, completed, failed
    start_time: float = 0.0
    end_time: float = 0.0
    events: List[DebugEvent] = field(default_factory=list)
    breakpoints: List[str] = field(default_factory=list)
    state_snapshots: Dict[str, Any] = field(default_factory=dict)

    def get_duration_ms(self) -> float:
        """Get execution duration."""
        return (self.end_time - self.start_time) * 1000 if self.end_time else 0

    def get_events_for_step(self, step_id: str) -> List[DebugEvent]:
        """Get all events for a specific step."""
        return [e for e in self.events if e.step_id == step_id]


class WorkflowDebugger:
    """Debugger for workflow execution."""

    def __init__(self):
        """Initialize debugger."""
        self.traces: Dict[str, WorkflowDebugTrace] = {}
        self.breakpoints: Dict[str, List[str]] = {}  # workflow_id -> step_ids
        self.paused_workflows: set = set()
        self.logger = logging.getLogger(__name__)

    def start_trace(
        self,
        workflow_id: str,
        workflow_name: str,
    ) -> WorkflowDebugTrace:
        """Start a new debug trace."""
        trace = WorkflowDebugTrace(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            start_time=time.time(),
        )
        self.traces[workflow_id] = trace
        return trace

    def add_event(
        self,
        workflow_id: str,
        event_type: str,
        step_id: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
    ) -> None:
        """Add a debug event."""
        if workflow_id not in self.traces:
            return

        event_id = f"{workflow_id}_{len(self.traces[workflow_id].events)}"
        event = DebugEvent(
            event_id=event_id,
            timestamp=time.time(),
            event_type=event_type,
            workflow_id=workflow_id,
            step_id=step_id,
            data=data or {},
            error=error,
            duration_ms=duration_ms,
        )

        self.traces[workflow_id].events.append(event)

    def set_breakpoint(self, workflow_id: str, step_id: str) -> None:
        """Set a breakpoint at a step."""
        if workflow_id not in self.breakpoints:
            self.breakpoints[workflow_id] = []
        if step_id not in self.breakpoints[workflow_id]:
            self.breakpoints[workflow_id].append(step_id)

    def should_break(self, workflow_id: str, step_id: str) -> bool:
        """Check if execution should pause at breakpoint."""
        return (
            workflow_id in self.breakpoints
            and step_id in self.breakpoints[workflow_id]
        )

    def pause_workflow(self, workflow_id: str) -> None:
        """Pause workflow execution."""
        self.paused_workflows.add(workflow_id)
        self.logger.info(f"Paused workflow: {workflow_id}")

    def resume_workflow(self, workflow_id: str) -> None:
        """Resume workflow execution."""
        self.paused_workflows.discard(workflow_id)
        self.logger.info(f"Resumed workflow: {workflow_id}")

    def is_paused(self, workflow_id: str) -> bool:
        """Check if workflow is paused."""
        return workflow_id in self.paused_workflows

    def get_trace(self, workflow_id: str) -> Optional[WorkflowDebugTrace]:
        """Get debug trace for workflow."""
        return self.traces.get(workflow_id)

    def end_trace(self, workflow_id: str, status: str = "completed") -> None:
        """End a debug trace."""
        if workflow_id in self.traces:
            self.traces[workflow_id].status = status
            self.traces[workflow_id].end_time = time.time()

    def get_step_timeline(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get step execution timeline."""
        if workflow_id not in self.traces:
            return []

        trace = self.traces[workflow_id]
        timeline = []

        for event in trace.events:
            timeline.append({
                "step_id": event.step_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "duration_ms": event.duration_ms,
                "error": event.error,
            })

        return timeline

    def get_execution_path(self, workflow_id: str) -> List[str]:
        """Get execution path (sequence of steps)."""
        if workflow_id not in self.traces:
            return []

        trace = self.traces[workflow_id]
        path = []

        for event in trace.events:
            if event.event_type == "step_enter":
                path.append(event.step_id)

        return path


class ExecutionProfiler:
    """Profiles workflow execution performance."""

    def __init__(self):
        """Initialize profiler."""
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def start_profiling(self, workflow_id: str) -> None:
        """Start profiling a workflow."""
        self.profiles[workflow_id] = {
            "start_time": time.time(),
            "steps": {},
            "total_time": 0,
        }

    def profile_step(
        self,
        workflow_id: str,
        step_id: str,
        duration_ms: float,
        memory_mb: float = 0.0,
    ) -> None:
        """Profile a step execution."""
        if workflow_id not in self.profiles:
            return

        if step_id not in self.profiles[workflow_id]["steps"]:
            self.profiles[workflow_id]["steps"][step_id] = {
                "count": 0,
                "total_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
                "avg_time": 0,
                "memory_mb": 0,
            }

        step_profile = self.profiles[workflow_id]["steps"][step_id]
        step_profile["count"] += 1
        step_profile["total_time"] += duration_ms
        step_profile["min_time"] = min(step_profile["min_time"], duration_ms)
        step_profile["max_time"] = max(step_profile["max_time"], duration_ms)
        step_profile["avg_time"] = step_profile["total_time"] / step_profile["count"]
        step_profile["memory_mb"] = memory_mb

    def get_profile_report(self, workflow_id: str) -> Dict[str, Any]:
        """Get execution profile report."""
        if workflow_id not in self.profiles:
            return {}

        profile = self.profiles[workflow_id]
        total_time = time.time() - profile["start_time"]

        # Find slowest steps
        steps_by_time = sorted(
            profile["steps"].items(),
            key=lambda x: x[1]["total_time"],
            reverse=True,
        )

        return {
            "workflow_id": workflow_id,
            "total_time_ms": total_time * 1000,
            "step_count": len(profile["steps"]),
            "steps": dict(steps_by_time),
            "slowest_step": steps_by_time[0][0] if steps_by_time else None,
            "slowest_step_time": steps_by_time[0][1]["total_time"] if steps_by_time else 0,
        }


class WorkflowValidator:
    """Validates workflow structure and execution."""

    def __init__(self):
        """Initialize validator."""
        self.logger = logging.getLogger(__name__)

    def validate_workflow(
        self,
        workflow_definition: Dict[str, Any],
    ) -> List[str]:
        """
        Validate workflow definition.

        Args:
            workflow_definition: Workflow structure

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        if "name" not in workflow_definition:
            errors.append("Workflow must have a name")

        if "steps" not in workflow_definition:
            errors.append("Workflow must have steps")
        else:
            steps = workflow_definition["steps"]

            # Validate each step
            for step_id, step in steps.items():
                if "type" not in step:
                    errors.append(f"Step {step_id} must have a type")

                # Check dependencies exist
                if "depends_on" in step:
                    for dep in step["depends_on"]:
                        if dep not in steps:
                            errors.append(f"Step {step_id} depends on undefined step {dep}")

        return errors

    def detect_deadlocks(
        self,
        workflow_definition: Dict[str, Any],
    ) -> List[str]:
        """Detect potential deadlocks in workflow."""
        issues = []
        steps = workflow_definition.get("steps", {})

        # Check for circular dependencies
        for step_id, step in steps.items():
            visited = set()
            if self._has_cycle(step_id, steps, visited):
                issues.append(f"Circular dependency detected involving step {step_id}")

        return issues

    def _has_cycle(
        self,
        step_id: str,
        steps: Dict[str, Dict[str, Any]],
        visited: set,
    ) -> bool:
        """Check if step has circular dependency."""
        if step_id in visited:
            return True

        visited.add(step_id)
        dependencies = steps.get(step_id, {}).get("depends_on", [])

        for dep in dependencies:
            if self._has_cycle(dep, steps, visited.copy()):
                return True

        return False
