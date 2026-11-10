# Homework_marking_system

This package is developed for BA course of MGT5493 visible notebook auto marking at University of Glasgow. It moves the feedback class and reusable table/plot assertions out of student using notebook. Each homework has a separate module defining its own references and checks. The public Lab 2 and Lab 3 modules are bundled, so students need only the package, notebook and dataset, with no extra helper file.

**Status:** testing prototype, version 0.2.0. Source is published on [GitHub](https://github.com/KrisrcQi/Homework_marking_system). The repository name is Homework_marking_system; the distribution name is homework-marking-system and the Python import name is homework_marking_system.

## Installation

Install from GitHub in a **Jupyter or VS Code notebook cell**:

```python
%pip install "homework-marking-system[tables,plots] @ git+https://github.com/KrisrcQi/Homework_marking_system.git@v0.2.0"
```

Or install from a **terminal**, using the Python environment for your notebook:

```bash
python3 -m pip install "homework-marking-system[tables,plots] @ git+https://github.com/KrisrcQi/Homework_marking_system.git@v0.2.0"
```

`%pip` is notebook syntax; do not type the `%` in a terminal. Git must be installed for these GitHub installation commands. Restart the notebook kernel after installation, then check the import:

```python
import homework_marking_system
print(homework_marking_system.__version__)
```

If pip reports `Did not find branch or tag`, such like v.0.1.0, please see the newest version of package tag on [GitHub](https://github.com/KrisrcQi/Homework_marking_system).

The core feedback class has no third-party runtime dependencies. The `tables` extra installs pandas/NumPy support; `plots` installs Matplotlib/NumPy support.
For Lab 2 without plot checks, `tables` is sufficient.
For Lab 3 plot checking is needed, `plots` is required.

### Local development

After downloading or cloning the repository, open a terminal in the folder containing pyproject.toml and run:

```bash
python3 -m pip install -e '.[tables,plots]'
```

This editable install uses your local source. Restart notebook kernels after editing or reinstalling code to avoid using previously imported definitions.

## Testing status by Lab2

Local verification completed with Python 3.11.7:

- All **14 package tests** passed, covering feedback, table comparisons and
  line/bar plot checks.
- The installed wheel was exercised in a fresh Jupyter kernel.
- All **26 Lab 2 checks** passed for the model answers: **90/90 visible marks**.
- A blank submission earned **0/90**; mismatched regional labels were rejected.
- The example keeps **10 manual marks** separate from automatic feedback.

This is a testing prototype. These checks do not establish compatibility with every Python version, operating system, dataset or plotting library. See VERIFICATION.json for the recorded local results. GitHub publication alone does not mean the package has passed automated CI or been released on PyPI.

## Simple visible marking

```python
from homework_marking_system import StudentFeedback, assert_frame

feedback = StudentFeedback({'load': 5, 'clean': 10}, manual_points=5)

with feedback.marks('load'):
    assert_frame(df, reference_df)

feedback.summarise_marks()
```

Each test ID must be unique. Rerunning a test replaces its earlier outcome; failures re-raise their exceptions so nbgrader can detect them. The summary distinguishes not run, failed, and passed. 

Hidden and manual points are shown separately and are never awarded by the visible summary.

Create feedback/marking only once per fresh notebook run. Recreating an object resets its outcomes. Use `feedback.reset()` to clear intentionally, or `new_assignment.reuse_results(old_assignment)` only when the checks, dataset and answers have not changed. Restart and Run All before trusting a result.

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

The assessment summary reports how many visible checks have run, how many marks have been earned, and whether all visible checks have passed. 

This is no submitted requirement for this homework. To get an up-to-date assessment, restart the kernel and run all notebook cells. Students can work on it multiple times till get full marks


References:
- Course of MGT5493: https://github.com/KrisrcQi/Programming_BA
- Python packaging: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- pip Git installation: https://pip.pypa.io/en/stable/topics/vcs-support/
- MIT license: https://opensource.org/license/mit
