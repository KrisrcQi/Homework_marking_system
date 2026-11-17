"""Public reference calculations and checks for Lab 4."""
import math

import numpy as np
import pandas as pd

from homework_marking_system import Assignment, Check, assert_frame, assert_series


def create_marking(data_path='product_performance.csv'):
    raw = pd.read_csv(data_path)
    margins = raw['Profit'] / raw['Sales'].replace(0, np.nan)
    expected_num = raw[['Sales', 'Cost', 'Profit']].assign(Profit_margin=margins)
    flags = pd.Series(np.select([margins.isna(), margins.ge(0.25)],
                               ['Unknown', 'High'], default='Low'), index=raw.index)
    flag_counts = flags.value_counts().reindex(['High', 'Low', 'Unknown'], fill_value=0)
    median = raw['Sales'].median()
    levels = pd.Series(np.where(raw['Sales'].ge(median), 'Above_med', 'Below_med'), index=raw.index)
    level_counts = levels.value_counts().reindex(['Above_med', 'Below_med'], fill_value=0)
    categories = raw.groupby('Category')
    counts = categories.size().to_dict()
    means = categories['Profit'].mean().to_dict()
    three_levels = pd.Series(np.select(
        [margins.isna(), margins.ge(0.30), margins.ge(0.15)],
        ['Unknown', 'Very_high', 'Medium'], default='Low'), index=raw.index)
    promotions = pd.Series(np.where(raw['Profit'].ge(80), 'Consider_Promotion', 'No_Need'), index=raw.index)
    promotion_summary = (raw.assign(Promotion=promotions).groupby(['Category', 'Promotion'])
                         .size().unstack(fill_value=0)
                         .reindex(columns=['Consider_Promotion', 'No_Need'], fill_value=0).sort_index())
    risks = pd.Series(np.select(
        [margins.isna(), margins.lt(0.15) & raw['Sales'].gt(median)],
        ['Unknown', 'High_Risk'], default='Low_Risk'), index=raw.index)

    def check_loaded(df):
        assert_frame(df, raw)

    def check_shape(data_shape):
        assert data_shape == raw.shape

    def check_head(first_5):
        assert_frame(first_5, raw.head())

    def check_statistics(data_statistics):
        assert_frame(data_statistics, raw.describe(), ignore_index=False)

    def check_margins(df_work):
        assert_frame(df_work, raw.assign(Profit_margin=margins))

    def check_numeric(df_num):
        assert_frame(df_num, expected_num)

    def check_flags(profit_flags):
        assert_series(profit_flags, flags, ignore_index=False)

    def check_flag_counts(profit_counts):
        assert_series(profit_counts, flag_counts, ignore_index=False)

    def check_median(median_sales):
        assert math.isclose(float(median_sales), median, rel_tol=1e-7)

    def check_levels(sales_levels):
        assert_series(sales_levels, levels, ignore_index=False)

    def check_level_counts(sales_counts):
        assert_series(sales_counts, level_counts, ignore_index=False)

    def check_category_counts(category_counts):
        assert isinstance(category_counts, dict)
        assert category_counts == counts

    def check_category_means(category_avg_profit):
        assert isinstance(category_avg_profit, dict)
        assert set(category_avg_profit) == set(means)
        for category, expected in means.items():
            assert math.isclose(category_avg_profit[category], expected, rel_tol=1e-7, abs_tol=1e-8)

    def check_margin_function(margin_check):
        assert callable(margin_check)
        for value, cutoff, expected in [
            (0.249, 0.25, 'Low'), (0.25, 0.25, 'High'),
            (-0.1, 0.25, 'Low'), (0.4, 0.5, 'Low'),
            (0.5, 0.5, 'High'), (np.nan, 0.25, 'Unknown'),
        ]:
            assert margin_check(value, cutoff) == expected
        assert margin_check(0.25) == 'High'

    def check_applied_margin(margin_labels):
        assert_series(margin_labels, flags, ignore_index=False)

    def check_category_function(profit_category):
        assert callable(profit_category)
        for value, expected in [(0.30, 'Very_high'), (0.299, 'Medium'),
                                (0.15, 'Medium'), (0.149, 'Low'),
                                (-0.1, 'Low'), (np.nan, 'Unknown')]:
            assert profit_category(value) == expected

    def check_applied_category(profit_categories):
        assert_series(profit_categories, three_levels, ignore_index=False)

    def check_promotions(promotion_flags):
        assert_series(promotion_flags, promotions, ignore_index=False)

    def check_promotion_table(promotion_summary_answer):
        assert_frame(promotion_summary_answer, promotion_summary, ignore_index=False)

    def check_risk_function(risk_flag):
        assert callable(risk_flag)
        for margin, sales, expected in [
            (0.149, 101, 'High_Risk'), (0.15, 101, 'Low_Risk'),
            (0.149, 100, 'Low_Risk'), (0.149, 99, 'Low_Risk'),
            (0.30, 101, 'Low_Risk'), (np.nan, 101, 'Unknown'),
        ]:
            row = pd.Series({'Profit_margin': margin, 'Sales': sales})
            assert risk_flag(row, 100) == expected

    def check_risk_results(risk_labels):
        assert_series(risk_labels, risks, ignore_index=False)

    return Assignment({
        'q1-data': Check(2, check_loaded),
        'q1-shape': Check(1, check_shape),
        'q1-head': Check(1, check_head),
        'q1-statistics': Check(1, check_statistics),
        'q2-margins': Check(6, check_margins),
        'q2-numeric': Check(4, check_numeric),
        'q3-labels': Check(6, check_flags),
        'q3-counts': Check(4, check_flag_counts),
        'q4-median': Check(2, check_median),
        'q4-labels': Check(5, check_levels),
        'q4-counts': Check(3, check_level_counts),
        'q5-counts': Check(7, check_category_counts),
        'q5-means': Check(8, check_category_means),
        'q6-margin-function': Check(4, check_margin_function),
        'q6-margin-apply': Check(3, check_applied_margin),
        'q6-category-function': Check(5, check_category_function),
        'q6-category-apply': Check(3, check_applied_category),
        'q7-flags': Check(5, check_promotions),
        'q7-summary': Check(5, check_promotion_table),
        'q8-function': Check(8, check_risk_function),
        'q8-apply': Check(7, check_risk_results),
    }, manual_points=10)
