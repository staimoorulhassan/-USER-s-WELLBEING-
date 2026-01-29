"""AI-related models for focus scores and summaries."""

from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field


@dataclass
class FocusScore:
    """AI-calculated focus score (0-100).

    Attributes:
        value: Numeric score from 0 to 100
        calculated_at: When the score was calculated
        activity_summary: Brief summary of activity analyzed
        trend: Trend indicator ('up', 'down', 'stable', 'none')
        previous_score: Previous score for trend calculation
    """

    value: float
    calculated_at: datetime
    activity_summary: str = ""
    trend: str = "none"
    previous_score: Optional[float] = None

    def __post_init__(self):
        """Validate score value."""
        # Ensure score is in valid range
        if self.value < 0:
            self.value = 0.0
        elif self.value > 100:
            self.value = 100.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "value": self.value,
            "calculated_at": self.calculated_at.isoformat(),
            "activity_summary": self.activity_summary,
            "trend": self.trend,
            "previous_score": self.previous_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FocusScore":
        """Create from dictionary (deserialization)."""
        return cls(
            value=data["value"],
            calculated_at=datetime.fromisoformat(data["calculated_at"]),
            activity_summary=data.get("activity_summary", ""),
            trend=data.get("trend", "none"),
            previous_score=data.get("previous_score"),
        )

    def get_color(self) -> str:
        """Get color code based on score value.

        Returns:
            Color name for UI display
        """
        if self.value >= 80:
            return "green"  # Excellent focus
        elif self.value >= 60:
            return "yellow"  # Good focus
        elif self.value >= 40:
            return "orange"  # Fair focus
        else:
            return "red"  # Poor focus

    def get_label(self) -> str:
        """Get text label based on score value.

        Returns:
            Label string
        """
        if self.value >= 80:
            return "Excellent"
        elif self.value >= 60:
            return "Good"
        elif self.value >= 40:
            return "Fair"
        else:
            return "Needs Improvement"


@dataclass
class DailySummary:
    """AI-generated daily summary of activity.

    Attributes:
        summary_text: Main summary text
        productivity_patterns: List of observed productivity patterns
        time_distribution: Dictionary mapping time periods to activities
        goal_alignment: Assessment of goal alignment
        recommendations: List of actionable recommendations
        generated_at: When the summary was generated
    """

    summary_text: str
    productivity_patterns: List[str] = field(default_factory=list)
    time_distribution: Dict[str, str] = field(default_factory=dict)
    goal_alignment: str = ""
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "summary_text": self.summary_text,
            "productivity_patterns": self.productivity_patterns,
            "time_distribution": self.time_distribution,
            "goal_alignment": self.goal_alignment,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DailySummary":
        """Create from dictionary (deserialization)."""
        return cls(
            summary_text=data["summary_text"],
            productivity_patterns=data.get("productivity_patterns", []),
            time_distribution=data.get("time_distribution", {}),
            goal_alignment=data.get("goal_alignment", ""),
            recommendations=data.get("recommendations", []),
            generated_at=datetime.fromisoformat(data["generated_at"]),
        )
