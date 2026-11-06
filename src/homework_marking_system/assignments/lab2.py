"""Homework-specific visible rules; bundled public Lab 2 example, separate from the generic engine.

All tests and reference calculations here are public. Keep hidden assessment
checks in the instructor's separate nbgrader source. Dataset not bundled.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from homework_marking_system import Assignment, Check
from homework_marking_system import assert_frame as _frame
from homework_marking_system import assert_series as _series
from homework_marking_system import assert_group as _group


def create_marking(data_path="retail_data.csv"):
    """Create an independent reference and a fresh 90-point marking session."""
    data_path = Path(data_path).resolve()
    _raw = pd.read_csv(data_path)
    _dedup = _raw.drop_duplicates(keep='first').copy()
    _clean = _dedup.copy()
    _clean['Region'] = _clean['Region'].fillna('Unknown')
    _clean['Category'] = _clean['Category'].fillna('Unknown')
    _cost = pd.to_numeric(_dedup['Cost'], errors='coerce')
    _clean['Cost'] = _cost.fillna(_cost.median())
    _clean['Date'] = pd.to_datetime(_clean['Date'], format='%d/%m/%Y')
    _clean['Year'] = _clean['Date'].dt.year
    _clean['Month'] = _clean['Date'].dt.month
    _clean['Month_name'] = _clean['Date'].dt.month_name()
    _region = _clean.groupby('Region', as_index=False)[['Sales', 'Profit']].sum()
    _category = _clean.groupby('Category').agg(Total_sales=('Sales', 'sum'), Total_profit=('Profit', 'sum'))
    _monthly = _clean.groupby(['Year', 'Month'])['Sales'].sum().sort_index()

    def _check_a_loaded_values(df):
        pd.testing.assert_frame_equal(df.reset_index(drop=True), pd.read_csv(data_path).reset_index(drop=True), check_dtype=False)

    def _check_b_first_ten(first_10):
        _frame(first_10, _raw.head(10))

    def _check_b_shape(data_shape):
        _visible_raw = pd.read_csv(data_path)
        assert data_shape == _visible_raw.shape

    def _check_b_column_names(column_names):
        assert column_names == pd.read_csv(data_path).columns.tolist()

    def _check_b_dtypes(data_types):
        pd.testing.assert_series_equal(data_types, _raw.dtypes)

    def _check_b_statistics(numeric_summary):
        pd.testing.assert_frame_equal(numeric_summary, _raw.describe(), check_dtype=False, check_exact=False, rtol=1e-07, atol=1e-08)

    def _check_c_missing_counts(missing_counts):
        pd.testing.assert_series_equal(missing_counts, _raw.isna().sum(), check_dtype=False, check_names=False)

    def _check_c_missing_rows(missing_rows):
        _frame(missing_rows, _raw.loc[_raw.isna().any(axis=1)])

    def _check_c_duplicate_count(duplicate_count):
        assert duplicate_count == int(_raw.duplicated().sum())

    def _check_c_duplicate_rows(duplicate_rows):
        _frame(duplicate_rows, _raw.loc[_raw.duplicated()])

    def _check_c_types(type_checks):
        pd.testing.assert_series_equal(type_checks, _raw[['Date', 'Sales', 'Cost', 'Profit']].dtypes)

    def _check_d_original_unchanged(df, df_clean):
        _frame(df, _raw)
        assert df_clean is not df

    def _check_d_deduplication(df_clean):
        assert len(df_clean) == len(_dedup)
        _frame(df_clean[['Product', 'Sales', 'Profit']], _dedup[['Product', 'Sales', 'Profit']])

    def _check_d_region(df_clean):
        _series(df_clean['Region'], _clean['Region'])

    def _check_d_category(df_clean):
        _series(df_clean['Category'], _clean['Category'])

    def _check_d_cost(df_clean):
        assert pd.api.types.is_numeric_dtype(df_clean['Cost'])
        _series(df_clean['Cost'], _clean['Cost'])

    def _check_d_dates(df_clean):
        assert pd.api.types.is_datetime64_any_dtype(df_clean['Date'])
        _series(df_clean['Date'], _clean['Date'])

    def _check_d_date_features(df_clean):
        _frame(df_clean[['Year', 'Month', 'Month_name']], _clean[['Year', 'Month', 'Month_name']])

    def _check_d_final_quality(df_clean):
        _visible_raw = pd.read_csv(data_path)
        assert df_clean.shape == (len(_visible_raw.drop_duplicates()), len(_visible_raw.columns) + 3)
        assert df_clean.columns.tolist() == _visible_raw.columns.tolist() + ['Year', 'Month', 'Month_name']
        assert not df_clean.isna().any().any()
        assert df_clean.duplicated().sum() == 0

    def _check_e_region_table(regional_summary):
        _group(regional_summary, _region, 'Sales', group_column='Region')

    def _check_e_region_leader(top_region):
        assert isinstance(top_region, str)
        assert top_region in _region.loc[_region['Sales'] == _region['Sales'].max(), 'Region'].tolist()

    def _check_e_category_table(category_summary):
        _group(category_summary, _category, 'Total_profit', value_columns=['Total_sales', 'Total_profit'])

    def _check_e_category_leader(top_category):
        assert isinstance(top_category, str)
        assert top_category in _category.index[_category['Total_profit'] == _category['Total_profit'].max()]

    def _check_f_monthly(monthly_sales):
        pd.testing.assert_series_equal(monthly_sales, _monthly, check_dtype=False, check_names=True, check_exact=False, rtol=1e-07, atol=1e-08)
        assert monthly_sales.index.is_monotonic_increasing

    def _check_f_export(df_clean):
        # Require this run's prepared answer as well as the file contents.
        _frame(df_clean, _clean)
        from pathlib import Path
        import io
        assert Path('retail_data_cleaned_homework.csv').is_file()
        _export_expected = pd.read_csv(io.StringIO(_clean.to_csv(index=False)))
        _export_actual = pd.read_csv('retail_data_cleaned_homework.csv')
        _frame(_export_actual, _export_expected)

    def _check_f_reloaded(df_reloaded):
        import io
        _frame(df_reloaded, pd.read_csv(io.StringIO(_clean.to_csv(index=False))))

    return Assignment({
        'a-loaded-values': Check(5, _check_a_loaded_values),
        'b-first-ten': Check(2, _check_b_first_ten),
        'b-shape': Check(1, _check_b_shape),
        'b-column-names': Check(1, _check_b_column_names),
        'b-dtypes': Check(2, _check_b_dtypes),
        'b-statistics': Check(4, _check_b_statistics),
        'c-missing-counts': Check(4, _check_c_missing_counts),
        'c-missing-rows': Check(4, _check_c_missing_rows),
        'c-duplicate-count': Check(2, _check_c_duplicate_count),
        'c-duplicate-rows': Check(2, _check_c_duplicate_rows),
        'c-types': Check(3, _check_c_types),
        'd-original-unchanged': Check(4, _check_d_original_unchanged),
        'd-deduplication': Check(5, _check_d_deduplication),
        'd-region': Check(3, _check_d_region),
        'd-category': Check(3, _check_d_category),
        'd-cost': Check(6, _check_d_cost),
        'd-dates': Check(6, _check_d_dates),
        'd-date-features': Check(6, _check_d_date_features),
        'd-final-quality': Check(2, _check_d_final_quality),
        'e-region-table': Check(6, _check_e_region_table),
        'e-region-leader': Check(1, _check_e_region_leader),
        'e-category-table': Check(6, _check_e_category_table),
        'e-category-leader': Check(2, _check_e_category_leader),
        'f-monthly': Check(5, _check_f_monthly),
        'f-export': Check(3, _check_f_export),
        'f-reloaded': Check(2, _check_f_reloaded),
    }, manual_points=10)
