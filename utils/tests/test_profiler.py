import polars as pl
from health_check.profiler import profile_dataframe

def test_profile_dataframe_basic():
    """
    Tests basic profiling of a simple dataframe.
    """
    df = pl.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": ["a", "b", "c", "d", "e"]
    })
    report = profile_dataframe(df)
    assert len(report) == 2
    assert report[0]["column_name"] == "a"
    assert report[1]["column_name"] == "b"
    assert report[0]["missing_values"] == 0
    assert report[0]["unique_values"] == 5
    assert "histogram" in report[0]

def test_profile_dataframe_with_dates():
    """
    Tests that date parsing works for a column with dates.
    """
    df = pl.DataFrame({
        "dates": ["2022-01-01", "2022-01-02", "2022-01-03", "not a date", None]
    })
    report = profile_dataframe(df)
    assert len(report) == 1
    date_profile = report[0]
    assert date_profile["column_name"] == "dates"
    assert date_profile["missing_values"] == 1
    assert "date_analysis" in date_profile
    assert date_profile["date_analysis"]["is_potential_date_column"] == True
    assert date_profile["date_analysis"]["parse_failure_count"] == 0

def test_profile_dataframe_histogram():
    """
    Tests that histogram data is generated for a numeric column.
    """
    df = pl.DataFrame({
        "numeric": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
    })
    report = profile_dataframe(df)
    assert len(report) == 1
    numeric_profile = report[0]
    assert "histogram" in numeric_profile
    assert "counts" in numeric_profile["histogram"]
    assert "bin_edges" in numeric_profile["histogram"]
    assert len(numeric_profile["histogram"]["counts"]) > 0
    assert len(numeric_profile["histogram"]["bin_edges"]) > 0
