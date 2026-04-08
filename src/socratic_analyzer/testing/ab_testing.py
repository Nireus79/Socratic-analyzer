"""A/B testing framework for learning experiments."""

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Status of an experiment."""

    PLANNING = "planning"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VariantAssignment(str, Enum):
    """Variant assignment strategy."""

    RANDOM = "random"
    SEQUENTIAL = "sequential"
    WEIGHTED = "weighted"
    CUSTOM = "custom"


@dataclass
class Variant:
    """Single experiment variant."""

    name: str
    description: str
    variant_id: str = ""
    weight: float = 0.5  # For weighted assignment
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize variant ID if not provided."""
        if not self.variant_id:
            self.variant_id = self.name.lower().replace(" ", "_")


@dataclass
class HypothesisResult:
    """Result of hypothesis testing."""

    hypothesis: str
    metric_name: str
    control_mean: float
    variant_mean: float
    control_std: float
    variant_std: float
    p_value: float
    confidence_level: float = 0.95
    is_significant: bool = False
    effect_size: float = 0.0  # Cohen's d
    sample_size_control: int = 0
    sample_size_variant: int = 0
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hypothesis": self.hypothesis,
            "metric_name": self.metric_name,
            "control_mean": self.control_mean,
            "variant_mean": self.variant_mean,
            "control_std": self.control_std,
            "variant_std": self.variant_std,
            "p_value": self.p_value,
            "confidence_level": self.confidence_level,
            "is_significant": self.is_significant,
            "effect_size": self.effect_size,
            "sample_size_control": self.sample_size_control,
            "sample_size_variant": self.sample_size_variant,
            "recommendation": self.recommendation,
        }


@dataclass
class ExperimentMetrics:
    """Metrics collected during experiment."""

    variant_id: str
    metric_name: str
    values: List[float] = field(default_factory=list)
    count: int = 0
    sum: float = 0.0
    mean: float = 0.0
    std_dev: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0

    def add_value(self, value: float) -> None:
        """Add a metric value."""
        self.values.append(value)
        self.count += 1
        self.sum += value
        self.mean = self.sum / self.count if self.count > 0 else 0

        if self.count > 1:
            variance = sum((x - self.mean) ** 2 for x in self.values) / self.count
            self.std_dev = variance**0.5

        self.min_value = min(self.values)
        self.max_value = max(self.values)


@dataclass
class ExperimentResult:
    """Complete result of an experiment."""

    experiment_id: str
    name: str
    status: ExperimentStatus
    variants: Dict[str, Variant]
    metrics: Dict[str, Dict[str, ExperimentMetrics]] = field(default_factory=dict)
    hypothesis_results: List[HypothesisResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    total_participants: int = 0
    confidence_level: float = 0.95
    duration_days: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "status": self.status.value,
            "variants": {k: {"name": v.name, "config": v.config} for k, v in self.variants.items()},
            "total_participants": self.total_participants,
            "hypothesis_results": [h.to_dict() for h in self.hypothesis_results],
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "confidence_level": self.confidence_level,
            "duration_days": self.duration_days,
        }


class ABTestingFramework:
    """Framework for designing and running A/B tests."""

    def __init__(self):
        """Initialize A/B testing framework."""
        self.experiments: Dict[str, ExperimentResult] = {}
        self.participant_assignments: Dict[str, str] = {}  # participant_id -> variant_id
        self.logger = logging.getLogger(__name__)

    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        variants: List[Variant],
        hypothesis: str,
        primary_metric: str,
        secondary_metrics: Optional[List[str]] = None,
        confidence_level: float = 0.95,
        duration_days: int = 7,
    ) -> ExperimentResult:
        """
        Create an A/B test experiment.

        Args:
            experiment_id: Unique experiment ID
            name: Human-readable experiment name
            variants: List of variants to test
            hypothesis: Hypothesis being tested
            primary_metric: Primary success metric
            secondary_metrics: Optional secondary metrics
            confidence_level: Statistical confidence level (default 0.95)
            duration_days: Expected duration of experiment

        Returns:
            ExperimentResult with experiment details
        """
        if experiment_id in self.experiments:
            raise ValueError(f"Experiment {experiment_id} already exists")

        if len(variants) < 2:
            raise ValueError("At least 2 variants required for A/B test")

        variants_dict = {v.variant_id: v for v in variants}
        metrics_dict: Dict[str, Dict[str, ExperimentMetrics]] = {}

        # Initialize metrics storage
        all_metrics = [primary_metric] + (secondary_metrics or [])
        for metric in all_metrics:
            metrics_dict[metric] = {
                v.variant_id: ExperimentMetrics(
                    variant_id=v.variant_id,
                    metric_name=metric,
                )
                for v in variants
            }

        result = ExperimentResult(
            experiment_id=experiment_id,
            name=name,
            status=ExperimentStatus.PLANNING,
            variants=variants_dict,
            metrics=metrics_dict,
            confidence_level=confidence_level,
            duration_days=duration_days,
        )

        self.experiments[experiment_id] = result
        self.logger.info(f"Created experiment: {name} ({experiment_id})")

        return result

    def assign_variant(
        self,
        experiment_id: str,
        participant_id: str,
        strategy: VariantAssignment = VariantAssignment.RANDOM,
        custom_fn: Optional[Callable] = None,
    ) -> str:
        """
        Assign participant to a variant.

        Args:
            experiment_id: Experiment ID
            participant_id: Participant ID
            strategy: Assignment strategy
            custom_fn: Custom assignment function

        Returns:
            Assigned variant ID
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]
        variants = list(experiment.variants.values())

        if strategy == VariantAssignment.RANDOM:
            variant = random.choice(variants)
        elif strategy == VariantAssignment.SEQUENTIAL:
            # Simple round-robin
            variant = variants[len(self.participant_assignments) % len(variants)]
        elif strategy == VariantAssignment.WEIGHTED:
            # Weighted random selection
            weights = [v.weight for v in variants]
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            variant = random.choices(variants, weights=normalized_weights, k=1)[0]
        elif strategy == VariantAssignment.CUSTOM:
            if custom_fn is None:
                raise ValueError("custom_fn required for CUSTOM strategy")
            variant_id = custom_fn(participant_id, variants)
            variant = next((v for v in variants if v.variant_id == variant_id), variants[0])
        else:
            raise ValueError(f"Unknown assignment strategy: {strategy}")

        self.participant_assignments[participant_id] = variant.variant_id
        return variant.variant_id

    def record_metric(
        self,
        experiment_id: str,
        participant_id: str,
        metric_name: str,
        value: float,
    ) -> None:
        """
        Record a metric value for a participant.

        Args:
            experiment_id: Experiment ID
            participant_id: Participant ID
            metric_name: Name of metric
            value: Metric value
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        if participant_id not in self.participant_assignments:
            raise ValueError(f"Participant {participant_id} not assigned to variant")

        experiment = self.experiments[experiment_id]
        variant_id = self.participant_assignments[participant_id]

        if metric_name not in experiment.metrics:
            raise ValueError(f"Metric {metric_name} not defined for experiment")

        experiment.metrics[metric_name][variant_id].add_value(value)

    def start_experiment(self, experiment_id: str) -> None:
        """Start an experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.utcnow()
        self.logger.info(f"Started experiment: {experiment.name}")

    def end_experiment(self, experiment_id: str) -> ExperimentResult:
        """
        End an experiment and calculate results.

        Args:
            experiment_id: Experiment ID

        Returns:
            Final ExperimentResult with analysis
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.ended_at = datetime.utcnow()

        if experiment.started_at:
            duration = experiment.ended_at - experiment.started_at
            experiment.duration_days = duration.days

        # Count total participants
        experiment.total_participants = len(self.participant_assignments)

        # Analyze results
        self._analyze_results(experiment)

        self.logger.info(f"Completed experiment: {experiment.name}")
        return experiment

    def _analyze_results(self, experiment: ExperimentResult) -> None:
        """Analyze experiment results and test hypotheses."""
        # Get first two variants for comparison (control vs treatment)
        variants = list(experiment.variants.values())
        if len(variants) < 2:
            return

        control_variant = variants[0]
        treatment_variant = variants[1]

        # Analyze each metric
        for metric_name, metric_data in experiment.metrics.items():
            control_metrics = metric_data[control_variant.variant_id]
            treatment_metrics = metric_data[treatment_variant.variant_id]

            if control_metrics.count == 0 or treatment_metrics.count == 0:
                continue

            # Calculate effect size (Cohen's d)
            pooled_std = (
                (
                    (control_metrics.count - 1) * control_metrics.std_dev**2
                    + (treatment_metrics.count - 1) * treatment_metrics.std_dev**2
                )
                / (control_metrics.count + treatment_metrics.count - 2)
            ) ** 0.5

            effect_size = (
                (treatment_metrics.mean - control_metrics.mean) / pooled_std
                if pooled_std > 0
                else 0
            )

            # Simple p-value calculation (placeholder for full statistical test)
            # In production, use scipy.stats.ttest_ind
            mean_diff = abs(treatment_metrics.mean - control_metrics.mean)
            p_value = 0.01 if mean_diff > 0.05 else 0.5  # Simplified

            is_significant = p_value < (1 - experiment.confidence_level)

            hypothesis = f"Treatment {treatment_variant.name} improves {metric_name}"
            recommendation = (
                f"Implement {treatment_variant.name}"
                if is_significant
                else "Continue testing or revert to control"
            )

            result = HypothesisResult(
                hypothesis=hypothesis,
                metric_name=metric_name,
                control_mean=control_metrics.mean,
                variant_mean=treatment_metrics.mean,
                control_std=control_metrics.std_dev,
                variant_std=treatment_metrics.std_dev,
                p_value=p_value,
                confidence_level=experiment.confidence_level,
                is_significant=is_significant,
                effect_size=effect_size,
                sample_size_control=control_metrics.count,
                sample_size_variant=treatment_metrics.count,
                recommendation=recommendation,
            )

            experiment.hypothesis_results.append(result)

    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get summary of experiment results.

        Args:
            experiment_id: Experiment ID

        Returns:
            Summary dictionary
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]

        return {
            "experiment_id": experiment_id,
            "name": experiment.name,
            "status": experiment.status.value,
            "total_participants": experiment.total_participants,
            "duration_days": experiment.duration_days,
            "variants": {v.variant_id: v.name for v in experiment.variants.values()},
            "hypothesis_results": [h.to_dict() for h in experiment.hypothesis_results],
            "significant_metrics": [
                h.metric_name for h in experiment.hypothesis_results if h.is_significant
            ],
        }

    def list_experiments(
        self,
        status: Optional[ExperimentStatus] = None,
    ) -> List[ExperimentResult]:
        """
        List all experiments.

        Args:
            status: Optional filter by status

        Returns:
            List of experiments
        """
        experiments = list(self.experiments.values())

        if status:
            experiments = [e for e in experiments if e.status == status]

        return experiments
