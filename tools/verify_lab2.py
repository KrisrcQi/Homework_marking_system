"""Run both example workflows on synthetic data; never touch teaching files."""
from pathlib import Path
import contextlib
import io
import json
import os
import sys
import tempfile
import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples/lab2'))
from make_demo_data import write_demo

instructor = nbformat.read(ROOT / 'examples/lab2/Homework_Lab2_instructor.ipynb', as_version=4)
student = nbformat.read(ROOT / 'examples/lab2/Homework_Lab2_student.ipynb', as_version=4)
models = {c.metadata.nbgrader.grade_id: c.source for c in instructor.cells
          if c.metadata.nbgrader.solution}
report = {}
previous = Path.cwd()
with tempfile.TemporaryDirectory(prefix='homework-package-example-') as tmp:
    os.chdir(tmp)
    try:
        write_demo('retail_data.csv')
        for mode in ['correct', 'blank']:
            # Each synthetic submission gets a clean output state.
            Path('retail_data_cleaned_homework.csv').unlink(missing_ok=True)
            ns = {}
            for c in student.cells:
                if c.cell_type != 'code':
                    continue
                code = models.get(c.metadata.nbgrader.grade_id, c.source) if mode == 'correct' else c.source
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        exec(code, ns)
                except Exception:
                    if mode == 'correct':
                        raise
            summary = ns['marking'].feedback.summary()
            expected = 90 if mode == 'correct' else 0
            assert summary['earned'] == expected, summary
            report[mode] = summary
            if mode == 'correct':
                assert summary['all_passed'] and len(summary['statuses']) == 26
                # A valid-looking table with swapped business labels must fail.
                wrong = ns['regional_summary'].copy()
                wrong['Region'] = wrong['Region'].iloc[::-1].to_numpy()
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        ns['marking'].check('e-region-table', regional_summary=wrong)
                    except AssertionError:
                        pass
                    else:
                        raise AssertionError('Mislabeled totals incorrectly passed')
                assert ns['marking'].feedback.summary()['earned'] == 84
                report['wrong_region_labels_rejected'] = True
    finally:
        os.chdir(previous)

print(json.dumps(report, indent=2))
