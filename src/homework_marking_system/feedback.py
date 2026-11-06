"""Core marking machinery; no third-party dependencies."""
from contextlib import contextmanager
from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Callable, Mapping


def _points(value):
    if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value) or value < 0:
        raise ValueError("Points must be a finite, nonnegative number")
    return value


class StudentFeedback:
    """Track each uniquely named check; reruns replace the previous result.

    Failed checks always re-raise their exception, including when nbgrader
    executes the cell. Results are provisional, in-memory student feedback.
    """

    def __init__(self, points: Mapping[str, Real], *, hidden_points=0, manual_points=0):
        self.available = dict(points)
        if any(not isinstance(k, str) or not k for k in self.available):
            raise ValueError("Every check needs a nonempty string ID")
        for p in self.available.values():
            _points(p)
        self.hidden_points = _points(hidden_points)
        self.manual_points = _points(manual_points)
        self.results = {}

    @contextmanager
    def marks(self, test_id):
        if test_id not in self.available:
            raise KeyError(f"Unknown marking test: {test_id}")
        points = self.available[test_id]
        self.results.pop(test_id, None)
        try:
            yield
        except Exception:
            self.results[test_id] = False
            print(f"❌ {test_id}: 0/{points} marks. Check the error below.")
            raise
        else:
            self.results[test_id] = True
            print(f"✅ {test_id}: {points}/{points} marks")

    def reset(self):
        self.results.clear()

    def summary(self):
        """Return structured results without printing or awarding manual marks."""
        statuses = {name: ("not run" if name not in self.results else
                           "passed" if self.results[name] else "failed")
                    for name in self.available}
        return {
            "earned": sum(p for k, p in self.available.items() if self.results.get(k) is True),
            "visible_total": sum(self.available.values()),
            "hidden_total": self.hidden_points,
            "manual_total": self.manual_points,
            "statuses": statuses,
            "all_passed": bool(self.available) and all(v == "passed" for v in statuses.values()),
        }

    def summarise_marks(self):
        result = self.summary()
        for name, status in result["statuses"].items():
            print(f"{name}: {status} ({self.available[name]} marks available)")
        print(f"Visible checks: {result['earned']}/{result['visible_total']}")
        if result["all_passed"]:
            print(f"✅ All {len(self.available)} visible tests passed.")
        print(f"Hidden marks: {self.hidden_points}; manual marks: {self.manual_points}.")
        print("Provisional: restart the kernel and Run All to check current answers.")
        return result


@dataclass(frozen=True)
class Check:
    points: Real
    function: Callable

    def __post_init__(self):
        _points(self.points)
        if not callable(self.function):
            raise TypeError("Check.function must be callable")


class Assignment:
    """Bundle an assignment's checks with their points and student feedback.

    Functions receive explicit student answers as keyword arguments. They must
    assert correctness or raise an exception. A False return also fails.
    Calling create_marking() again creates a fresh session: do that only once
    per run, or use reuse_results() to intentionally preserve an earlier session.
    """

    def __init__(self, checks: Mapping[str, Check], *, hidden_points=0, manual_points=0):
        self.checks = dict(checks)
        if any(not isinstance(c, Check) for c in self.checks.values()):
            raise TypeError("Each assignment entry must be a Check")
        self.feedback = StudentFeedback(
            {name: c.points for name, c in self.checks.items()},
            hidden_points=hidden_points, manual_points=manual_points,
        )

    def check(self, test_id, **answers):
        with self.feedback.marks(test_id):
            result = self.checks[test_id].function(**answers)
            if result is False:
                raise AssertionError("Check returned False")

    def summarise_marks(self):
        return self.feedback.summarise_marks()

    def reset(self):
        self.feedback.reset()

    def reuse_results(self, previous):
        """Explicitly copy outcomes after recreating an unchanged assignment.

        Point IDs and weights must match. Use a fresh kernel instead whenever
        checks, datasets, or answers change; matching IDs do not prove freshness.
        """
        if self.feedback.available != previous.feedback.available:
            raise ValueError("Cannot reuse results with different check IDs or marks")
        self.feedback.results = previous.feedback.results.copy()
        return self

