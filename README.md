# Homework_marking_system

A small MIT-licensed Python package for visible notebook marking. It moves the
feedback class and reusable table/plot assertions out of your notebook. Each
homework has a separate module defining its own references and checks. The
public Lab 2 module is bundled, so students need only the package, notebook
and dataset, with no extra helper file.

**Status:** local prototype, version 0.1.0. Not published on GitHub or PyPI yet.
The draft repository name is Homework_marking_system; the distribution name
is homework-marking-system and the import name is homework_marking_system.

## Install locally

In a terminal, from this repository folder:

```bash
python3 -m pip install -e '.[tables,plots]'
```

In a notebook, `%pip` installs into the current notebook kernel. Restart that
kernel after installation. The core feedback class has no third-party runtime
dependencies; table and plot support use the optional extras above.

Once this repository is published with a v0.1.0 tag, a student can install
directly from GitHub (replace YOUR_USERNAME with the real repository owner):

```python
%pip install "homework-marking-system[tables,plots] @ git+https://github.com/YOUR_USERNAME/Homework_marking_system.git@v0.1.0"
```

That is a future installation example, not a currently available repository.
Students do not need a PyPI release to install from GitHub. A command such as
`pip install homework-marking-system` requires a separate PyPI publication.
Use a fixed release tag or full commit for a class rather than a moving branch.

## Simple visible marking

```python
from homework_marking_system import StudentFeedback, assert_frame

feedback = StudentFeedback({'load': 5, 'clean': 10}, manual_points=5)

with feedback.marks('load'):
    assert_frame(df, reference_df)

feedback.summarise_marks()
```

Each test ID must be unique. Rerunning a test replaces its earlier outcome;
failures re-raise their exceptions so nbgrader can detect them. The summary
distinguishes not run, failed, and passed. Hidden and manual points are shown
separately and are never awarded by the visible summary.

Create feedback/marking only once per fresh notebook run. Recreating an object
resets its outcomes. Use `feedback.reset()` to clear intentionally, or
`new_assignment.reuse_results(old_assignment)` only when the checks, dataset
and answers have not changed. Restart and Run All before trusting a result.
Saved outputs are not live evidence that current answers passed.

## Keep the first two notebook cells short

The included Lab 2 example replaces both large setup cells with:

```python
import pandas as pd
import numpy as np
from homework_marking_system.assignments.lab2 import create_marking

marking = create_marking('retail_data.csv')
```

Student answers remain in normal cells. Each teacher test becomes one call:

```python
marking.check('a-loaded-values', df=df)
marking.check('e-region-table', regional_summary=regional_summary)
marking.summarise_marks()
```

`src/homework_marking_system/assignments/lab2.py` contains the public
course-specific checks and references, separate from the general engine.
The package contains no retail data or student submissions. Copy your course's
retail_data.csv into examples/lab2 before running the example notebooks, or
run `python3 examples/lab2/make_demo_data.py` to create original synthetic demo
data. The course's retail dataset is deliberately not included in this repository.

The example has 26 checks, 90 visible marks and 10 written/manual marks. Region
is a column with Sales/Profit totals. Category is an index with Total_sales and
Total_profit columns. This example consistently uses median Cost imputation,
after deduplication. It does not change your existing Lab2_Homework files.

Open `examples/lab2/Homework_Lab2_demo_executed.ipynb` to inspect a completed
example with outputs produced from the synthetic demo dataset. The student
notebook has no solutions or saved outputs. Package installation is still
required before running either notebook.

## Add new homework or logic checks

```python
from homework_marking_system import Assignment, Check

def check_discount(discount):
    assert 0 <= discount <= 1, 'Discount must be between 0 and 1'

def create_marking():
    return Assignment({'discount': Check(3, check_discount)}, manual_points=2)

# In the student notebook:
marking = create_marking()
marking.check('discount', discount=0.15)
```

Use separate named checks for independently awarded criteria. Check functions
must assert correctness or raise an error; an explicit False return fails too.
A new assignment can supply rules in its own companion module without changing
the engine. If you choose to bundle those rules under assignments/ like Lab 2,
changing them requires releasing a new package version for students to install.

## Table checks

```python
from homework_marking_system import assert_group

assert_group(regional_summary, expected_regions, 'Sales', group_column='Region')
assert_group(category_summary, expected_categories, 'Total_profit',
             value_columns=['Total_sales', 'Total_profit'])
```

These compare group labels and totals, required column names/order, and sorting.
Tied values may appear in either order. `assert_frame` and `assert_series` ignore
row indices by default; use ignore_index=False when index labels carry meaning.
Numeric comparisons have configurable tolerances.

## Plot checks

```python
from homework_marking_system import assert_line_plot, assert_bar_plot

assert_line_plot(ax, [1, 2, 3], [100, 150, 120],
                 xlabel='Month', ylabel='Sales', line_count=1)
assert_bar_plot(ax, [100, 150], tick_labels=['North', 'South'])
```

Line checks currently support numeric x/y values. Bar checks support a single
vertical bar chart. They assess data, order and optional labels rather than
pixel screenshots. For a different chart or business interpretation, write a
custom check function. The package cannot automatically determine whether any
arbitrary plot or logic is correct without teacher-specified expectations.

## Visible feedback and final grades

Public tests and references are readable, including when distributed in a pip
package. Packaging makes notebooks shorter; it does not hide answers. Keep
hidden tests in a separate instructor environment. Use trusted course tests and
dataset copies for final nbgrader runs, rather than trusting student-modified
packages or their saved summaries. This library does not sandbox student code.

Points in a notebook's nbgrader metadata must match the corresponding Check
points. The examples already do. If you change points in the course module,
update that notebook's test metadata and regenerate the release too.

## Development and publication

```bash
python3 -m unittest discover -s tests -v
python3 tools/verify_lab2.py
python3 -m pip install build
python3 -m build
```

Publish only this repository, not the surrounding teaching workspace. Do not
include gradebook.db, submissions, backups, or confidential tests. The MIT
license covers this project's code; third-party datasets need their own reuse
permission. The draft copyright notice names the project contributors; adjust
it to your desired copyright holder before publication.

Create a GitHub repository called Homework_marking_system, upload this project,
and tag a verified release v0.1.0. Publishing has not been performed by this
prototype. No package name availability on PyPI is implied.
See PUBLISHING.md for the concrete GitHub upload and tagged-install steps.

References:
- Python packaging: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- pip Git installation: https://pip.pypa.io/en/stable/topics/vcs-support/
- MIT license: https://opensource.org/license/mit
