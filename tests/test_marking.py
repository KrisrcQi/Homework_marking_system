import contextlib
import io
import math
import unittest

from homework_marking_system import Assignment, Check, StudentFeedback


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.redirect = contextlib.redirect_stdout(self.output)
        self.redirect.__enter__()

    def tearDown(self):
        self.redirect.__exit__(None, None, None)

    def test_pending_is_not_passed_and_manual_is_not_awarded(self):
        f = StudentFeedback({'load': 5, 'clean': 3}, manual_points=10)
        with f.marks('load'):
            pass
        s = f.summary()
        self.assertEqual(s['earned'], 5)
        self.assertEqual(s['visible_total'], 8)
        self.assertEqual(s['statuses']['clean'], 'not run')
        self.assertFalse(s['all_passed'])

    def test_rerunning_replaces_pass_with_failure_without_hiding_error(self):
        f = StudentFeedback({'a': 5, 'b': 2})
        with f.marks('a'):
            pass
        with self.assertRaisesRegex(AssertionError, 'wrong'):
            with f.marks('a'):
                raise AssertionError('wrong')
        with f.marks('b'):
            pass
        self.assertEqual(f.summary()['earned'], 2)
        self.assertEqual(f.summary()['statuses']['a'], 'failed')
        for _ in range(3):
            with f.marks('a'):
                pass
        self.assertEqual(f.summary()['earned'], 7)

    def test_unknown_id_does_not_erase_other_results(self):
        f = StudentFeedback({'a': 5})
        with f.marks('a'):
            pass
        with self.assertRaises(KeyError):
            with f.marks('typo'):
                pass
        self.assertEqual(f.summary()['earned'], 5)

    def test_interrupt_does_not_leave_previous_pass(self):
        f = StudentFeedback({'a': 5})
        with f.marks('a'):
            pass
        with self.assertRaises(KeyboardInterrupt):
            with f.marks('a'):
                raise KeyboardInterrupt()
        self.assertEqual(f.summary()['statuses']['a'], 'not run')

    def test_invalid_points_rejected(self):
        for points in [-1, math.nan, math.inf, True, 'five']:
            with self.subTest(points=points), self.assertRaises(ValueError):
                StudentFeedback({'a': points})

    def test_zero_point_check_still_tracks_status(self):
        f = StudentFeedback({'format': 0})
        with f.marks('format'):
            pass
        self.assertTrue(f.summary()['all_passed'])
        f.reset()
        self.assertFalse(f.summary()['all_passed'])

    def test_custom_logic_and_false_return(self):
        def positive(value):
            assert value > 0, 'Must be positive'
        a = Assignment({'positive': Check(3, positive)}, manual_points=2)
        a.check('positive', value=1)
        with self.assertRaises(AssertionError):
            a.check('positive', value=-1)
        self.assertEqual(a.feedback.summary()['earned'], 0)
        b = Assignment({'bad': Check(1, lambda: False)})
        with self.assertRaises(AssertionError):
            b.check('bad')

    def test_explicit_reuse_requires_same_rubric(self):
        a = Assignment({'x': Check(2, lambda: None)})
        a.check('x')
        b = Assignment({'x': Check(2, lambda: None)}).reuse_results(a)
        self.assertEqual(b.feedback.summary()['earned'], 2)
        with self.assertRaises(ValueError):
            Assignment({'x': Check(3, lambda: None)}).reuse_results(a)


class TableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pandas as pd
        except ImportError:
            raise unittest.SkipTest('Optional tables dependencies not installed')
        cls.pd = pd

    def test_frame_ignores_row_labels_but_not_missing_rows(self):
        from homework_marking_system import assert_frame
        expected = self.pd.DataFrame({'x': [1., 2.]})
        assert_frame(expected.set_axis([7, 8]), expected)
        with self.assertRaises(AssertionError):
            assert_frame(expected.iloc[:1], expected)

    def test_series_can_preserve_business_labels(self):
        from homework_marking_system import assert_series
        a = self.pd.Series([1, 2], index=['North', 'South'])
        b = a.set_axis(['South', 'North'])
        with self.assertRaises(AssertionError):
            assert_series(a, b, ignore_index=False)

    def test_region_column_matches_labels_and_rejects_wrong_sort(self):
        from homework_marking_system import assert_group
        e = self.pd.DataFrame({'Region': ['South', 'North'], 'Sales': [8., 4.], 'Profit': [2., 1.]})
        assert_group(e, e, 'Sales', group_column='Region')
        wrongs = [e.sort_values('Sales'), e.set_index('Region'),
                  e.assign(Region=['North', 'South']), e.assign(Region=['South', 'South'])]
        for wrong in wrongs:
            with self.subTest(), self.assertRaises(AssertionError):
                assert_group(wrong, e, 'Sales', group_column='Region')

    def test_category_renamed_totals_and_ties(self):
        from homework_marking_system import assert_group
        e = self.pd.DataFrame({'Total_sales': [10., 20.], 'Total_profit': [5., 5.]}, index=['A', 'B'])
        cols = ['Total_sales', 'Total_profit']
        assert_group(e.iloc[::-1], e, 'Total_profit', value_columns=cols)
        with self.assertRaises(AssertionError):
            assert_group(e.rename(columns={'Total_sales': 'Sales'}), e, 'Total_profit', value_columns=cols)


class PlotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except ImportError:
            raise unittest.SkipTest('Optional plot dependencies not installed')
        cls.plt = plt

    def tearDown(self):
        self.plt.close('all')

    def test_line_data_labels_and_count(self):
        from homework_marking_system import assert_line_plot
        _, ax = self.plt.subplots()
        ax.plot([1, 2], [10, 20])
        ax.set_xlabel('Month')
        assert_line_plot(ax, [1, 2], [10, 20], xlabel='Month', line_count=1)
        for options in [{'y': [20, 10]}, {'xlabel': 'Region'}, {'line_count': 2}]:
            args = dict(x=[1, 2], y=[10, 20]); args.update(options)
            with self.subTest(), self.assertRaises(AssertionError):
                assert_line_plot(ax, **args)

    def test_bar_heights_and_category_order(self):
        from homework_marking_system import assert_bar_plot
        _, ax = self.plt.subplots()
        ax.bar(['North', 'South'], [2, 5])
        assert_bar_plot(ax, [2, 5], tick_labels=['North', 'South'])
        with self.assertRaises(AssertionError):
            assert_bar_plot(ax, [5, 2])
        with self.assertRaises(AssertionError):
            assert_bar_plot(ax, [2, 5], tick_labels=['South', 'North'])


if __name__ == '__main__':
    unittest.main()
