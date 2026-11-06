"""Matplotlib checks on plotted data, not pixel screenshots.

These helpers check the explicit properties requested by the teacher. They do
not automatically judge whether a plot communicates a sensible business claim.
"""


def _numpy():
    try:
        import numpy as np
    except ImportError as exc:
        raise ImportError("Install homework-marking-system[plots] for plot checks") from exc
    return np


def _labels(ax, xlabel, ylabel, title):
    if xlabel is not None:
        assert ax.get_xlabel() == xlabel, "Incorrect x-axis label"
    if ylabel is not None:
        assert ax.get_ylabel() == ylabel, "Incorrect y-axis label"
    if title is not None:
        assert ax.get_title() == title, "Incorrect plot title"


def assert_line_plot(ax, x, y, *, line_index=0, line_count=None,
                     xlabel=None, ylabel=None, title=None, rtol=1e-7, atol=1e-8):
    """Check one numeric Matplotlib line and optional labels/line count."""
    np = _numpy()
    lines = ax.get_lines()
    if line_count is not None:
        assert len(lines) == line_count, "Incorrect number of lines"
    assert 0 <= line_index < len(lines), "Expected line is missing"
    np.testing.assert_allclose(lines[line_index].get_xdata(), x, rtol=rtol, atol=atol)
    np.testing.assert_allclose(lines[line_index].get_ydata(), y, rtol=rtol, atol=atol)
    _labels(ax, xlabel, ylabel, title)


def assert_bar_plot(ax, heights, *, xlabel=None, ylabel=None, title=None,
                    tick_labels=None, rtol=1e-7, atol=1e-8):
    """Check heights/order of a single vertical bar chart and optional labels.

    Stacked, grouped, and horizontal bar charts require their own custom check.
    """
    np = _numpy()
    actual = [p.get_height() for p in ax.patches]
    np.testing.assert_allclose(actual, heights, rtol=rtol, atol=atol)
    if tick_labels is not None:
        assert [t.get_text() for t in ax.get_xticklabels()] == list(tick_labels), "Incorrect bar labels or label order"
    _labels(ax, xlabel, ylabel, title)
