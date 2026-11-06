"""Pandas comparisons. Install the optional [tables] dependencies."""


def _pandas():
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("Install homework-marking-system[tables] for table checks") from exc
    return pd


def assert_frame(actual, expected, *, ignore_index=True, check_dtype=False,
                 rtol=1e-7, atol=1e-8):
    pd = _pandas()
    assert isinstance(actual, pd.DataFrame), "Expected a pandas DataFrame"
    assert isinstance(expected, pd.DataFrame), "Reference must be a DataFrame"
    if ignore_index:
        actual, expected = actual.reset_index(drop=True), expected.reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, expected, check_dtype=check_dtype,
                                 check_exact=False, rtol=rtol, atol=atol)


def assert_series(actual, expected, *, ignore_index=True, check_dtype=False,
                  check_names=False, rtol=1e-7, atol=1e-8):
    pd = _pandas()
    assert isinstance(actual, pd.Series), "Expected a pandas Series"
    assert isinstance(expected, pd.Series), "Reference must be a Series"
    if ignore_index:
        actual, expected = actual.reset_index(drop=True), expected.reset_index(drop=True)
    pd.testing.assert_series_equal(actual, expected, check_dtype=check_dtype,
        check_names=check_names, check_exact=False, rtol=rtol, atol=atol)


def assert_group(actual, expected, sort_column, *, group_column=None,
                 value_columns=None, ascending=False, rtol=1e-7, atol=1e-8):
    """Compare labels/totals and ordering, allowing ties in either order.

    group_column=None means group labels are in the index; otherwise require
    a normal grouping column. Pass value_columns to require renamed totals.
    """
    pd = _pandas()
    assert isinstance(actual, pd.DataFrame), "Expected a pandas DataFrame"
    value_columns = list(value_columns) if value_columns is not None else ["Sales", "Profit"]
    if group_column is not None:
        assert list(actual.columns) == [group_column] + value_columns, "Incorrect columns or column order"
        assert actual[group_column].notna().all(), "Missing group labels"
        assert not actual[group_column].duplicated().any(), "Repeated group labels"
        a, e = actual.set_index(group_column), expected.set_index(group_column)
    else:
        assert list(actual.columns) == value_columns, "Incorrect columns or column order"
        assert actual.index.is_unique, "Repeated group labels"
        a, e = actual, expected
    pd.testing.assert_frame_equal(a.sort_index(), e.sort_index(),
        check_dtype=False, check_names=False, check_exact=False, rtol=rtol, atol=atol)
    ordered = actual[sort_column]
    assert (ordered.is_monotonic_increasing if ascending else ordered.is_monotonic_decreasing), "Incorrect table sort order"

