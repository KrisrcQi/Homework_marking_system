"""Reusable checks and visible feedback for notebook assignments."""
from .feedback import Assignment, Check, StudentFeedback
from .tables import assert_frame, assert_group, assert_series
from .plots import assert_bar_plot, assert_line_plot

__version__ = "0.2.0"
__all__ = [
    "Assignment", "Check", "StudentFeedback", "assert_frame", "assert_series",
    "assert_group", "assert_line_plot", "assert_bar_plot",
]

