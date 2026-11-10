"""Visible checks for Lab 3 using the supplied marketing data."""

from io import StringIO

import numpy as np
import pandas as pd
from matplotlib.collections import PathCollection
from matplotlib.container import BarContainer

from homework_marking_system import Assignment, Check, assert_bar_plot, assert_frame, assert_series


MANUAL_POINTS = 15
CORRELATION_COLUMNS = ['Spend', 'Leads', 'Sales', 'Impressions', 'Clicks']


def _check_labels(ax, xlabel, ylabel):
    assert ax.get_xlabel() == xlabel, f'Use {xlabel!r} as the x-axis label'
    assert ax.get_ylabel() == ylabel, f'Use {ylabel!r} as the y-axis label'


def _leader_options(values, *, largest=True):
    valid = values.dropna()
    best = valid.max() if largest else valid.min()
    return set(valid.index[valid.eq(best)])


def create_marking(data_path='marketing_performance.csv'):
    raw = pd.read_csv(data_path)
    clean = raw.assign(Region=raw['Region'].fillna('Unknown'))
    info = StringIO()
    raw.info(buf=info, memory_usage=False)
    expected_info = info.getvalue()

    # groupby sorts names alphabetically, and stable sorting preserves ties.
    sales_by_channel = clean.groupby('Channel')['Sales'].sum().sort_values(
        ascending=False, kind='stable'
    )
    top5 = sales_by_channel.head(5)
    region_totals = clean.groupby('Region')[['Spend', 'Sales']].sum()
    months = pd.to_datetime(clean['Month']).dt.to_period('M').dt.to_timestamp()
    monthly_sales = clean.groupby(months)['Sales'].sum().sort_index()
    correlation = clean[CORRELATION_COLUMNS].corr()
    scatter_data = clean[['Impressions', 'Clicks']].to_numpy(dtype=float)
    scatter_data = scatter_data[np.isfinite(scatter_data).all(axis=1)]

    channel_totals = clean.groupby('Channel')[['Clicks', 'Impressions', 'Spend', 'Leads']].sum()
    channel_rates = pd.DataFrame({
        'CTR': channel_totals['Clicks'] / channel_totals['Impressions'].replace(0, np.nan),
        'CPL': channel_totals['Spend'] / channel_totals['Leads'].replace(0, np.nan),
    })
    region_ratios = region_totals[['Sales', 'Spend']].copy()
    region_ratios['Sales_to_Spend'] = region_ratios['Sales'] / region_ratios['Spend'].replace(0, np.nan)

    def check_data(df):
        assert_frame(df, clean)

    def check_head(first_5):
        assert_frame(first_5, raw.head())

    def check_shape(data_shape):
        assert data_shape == raw.shape, (
            f"Expected {raw.shape[0]} rows and {raw.shape[1]} columns"
            )

    def check_statistics(data_statis):
        assert_frame(data_statis, raw.describe(), ignore_index=False)

    def check_missing(data_missing_summary):
        assert_series(data_missing_summary, raw.isna().sum(), ignore_index=False)

    def check_channel_bar(ax_channel_sales):
        assert_bar_plot(ax_channel_sales, sales_by_channel.to_numpy(),
                        tick_labels=sales_by_channel.index.tolist(), xlabel='Channel', ylabel='Sales')

    def check_region_bars(ax_region_spend_sales):
        ax = ax_region_spend_sales
        _check_labels(ax, 'Region', 'Total value')
        labels = [tick.get_text() for tick in ax.get_xticklabels()]
        assert sorted(labels) == sorted(region_totals.index), 'Show each region once'
        containers = [c for c in ax.containers if isinstance(c, BarContainer)]
        series = {c.get_label(): c for c in containers}
        assert len(containers) == 2 and set(series) == {'Spend', 'Sales'}, 'Label both bar series'

        ticks = np.asarray(ax.get_xticks())
        assert len(ticks) == len(labels)
        # Order by physical position, so reversed construction order is fine.
        for label, container in series.items():
            assert container.orientation == 'vertical', 'Use vertical bars'
            bars = sorted(container.patches, key=lambda bar: bar.get_x() + bar.get_width() / 2)
            assert len(bars) == len(labels)
            np.testing.assert_allclose([bar.get_height() for bar in bars], region_totals.loc[labels, label])
            container_centres = np.array([bar.get_x() + bar.get_width() / 2 for bar in bars])
            nearest = np.abs(container_centres[:, None] - ticks).argmin(axis=1)
            np.testing.assert_array_equal(nearest, np.arange(len(labels)), err_msg='Align each bar with its region')

        spend = sorted(series['Spend'].patches, key=lambda bar: bar.get_x())
        sales = sorted(series['Sales'].patches, key=lambda bar: bar.get_x())
        for first, second in zip(spend, sales):
            left, right = sorted((first, second), key=lambda bar: bar.get_x())
            assert left.get_width() > 0 and right.get_width() > 0
            assert left.get_x() + left.get_width() <= right.get_x() + 1e-8, 'Place bars side by side'
        legend = ax.get_legend()
        assert legend is not None and {t.get_text() for t in legend.get_texts()} == {'Spend', 'Sales'}

    def check_monthly_line(ax_monthly_sales):
        _check_labels(ax_monthly_sales, 'Month', 'Sales')
        lines = ax_monthly_sales.get_lines()
        assert len(lines) == 1, 'Plot one monthly Sales line'
        x = lines[0].get_xdata()
        assert not pd.api.types.is_numeric_dtype(np.asarray(x).dtype), 'Plot dates on the x-axis'
        np.testing.assert_array_equal(
            pd.DatetimeIndex(pd.to_datetime(x)).to_numpy(dtype='datetime64[ns]'),
            monthly_sales.index.to_numpy(dtype='datetime64[ns]'),
        )
        np.testing.assert_allclose(lines[0].get_ydata(), monthly_sales.to_numpy())

    def check_heatmap(ax_correlation):
        images = ax_correlation.get_images()
        assert len(images) == 1, 'Create the heatmap with imshow'
        array = np.ma.asarray(images[0].get_array(), dtype=float).filled(np.nan)
        np.testing.assert_allclose(array, correlation.to_numpy(), equal_nan=True)
        for ticks in (ax_correlation.get_xticklabels(), ax_correlation.get_yticklabels()):
            assert [label.get_text() for label in ticks] == CORRELATION_COLUMNS

    def check_channel_rates(by_chan):
        assert list(by_chan.columns) == ['Channel', 'CTR', 'CPL']
        assert_frame(by_chan.set_index('Channel').sort_index(), channel_rates, ignore_index=False)

    def check_best_ctr(max_ctr_channel):
        assert max_ctr_channel in _leader_options(channel_rates['CTR'])

    def check_lowest_cpl(min_cpl_channel):
        assert min_cpl_channel in _leader_options(channel_rates['CPL'], largest=False)

    def check_region_ratios(by_region):
        assert_frame(by_region.sort_index(), region_ratios, ignore_index=False)

    def check_best_region(max_ratio_region):
        assert max_ratio_region in _leader_options(region_ratios['Sales_to_Spend'])

    def check_top5_data(top5_channel):
        assert_series(top5_channel, top5, ignore_index=False)

    def check_top5_bar(ax_top5):
        assert_bar_plot(ax_top5, top5.to_numpy(), tick_labels=top5.index.tolist(), xlabel='Channel', ylabel='Sales')

    def check_scatter(ax_scatter):
        _check_labels(ax_scatter, 'Impressions', 'Clicks')
        collections = [c for c in ax_scatter.collections if isinstance(c, PathCollection)]
        assert collections, 'Create a scatter plot'
        points = np.concatenate([
            np.ma.asarray(c.get_offsets(), dtype=float).filled(np.nan) for c in collections
        ])
        points = points[np.isfinite(points).all(axis=1)]
        actual = points[np.lexsort((points[:, 1], points[:, 0]))]
        expected = scatter_data[np.lexsort((scatter_data[:, 1], scatter_data[:, 0]))]
        np.testing.assert_allclose(actual, expected)

    return Assignment({
        'p1-data': Check(1, check_data),
        'p1-first-five': Check(1, check_head),
        'p1-shape': Check(1, check_shape),
        'p1-statistics': Check(1, check_statistics),
        'p1-missing': Check(1, check_missing),
        'p2-channel-sales': Check(10, check_channel_bar),
        'p2-region-bars': Check(10, check_region_bars),
        'p2-monthly-line': Check(10, check_monthly_line),
        'p2-heatmap': Check(10, check_heatmap),
        'p3-channel-rates': Check(6, check_channel_rates),
        'p3-best-ctr': Check(2, check_best_ctr),
        'p3-lowest-cpl': Check(2, check_lowest_cpl),
        'p4-region-ratios': Check(4, check_region_ratios),
        'p4-best-region': Check(6, check_best_region),
        'p5-top-five': Check(5, check_top5_data),
        'p5-bar': Check(5, check_top5_bar),
        'p6-scatter': Check(10, check_scatter),
    }, manual_points=MANUAL_POINTS)
