import polars as pl
from typing import List, Dict, Any
import dateparser

def get_column_profile(df: pl.DataFrame, column_name: str) -> Dict[str, Any]:
    """
    Generates a detailed profile for a single column in a DataFrame.

    Args:
        df: The Polars DataFrame.
        column_name: The name of the column to profile.

    Returns:
        A dictionary containing the profile of the column.
    """
    col = df[column_name]
    total_count = len(df)

    # Basic stats
    null_count = col.null_count()
    if total_count > 0:
        missing_percentage = (null_count / total_count) * 100
    else:
        missing_percentage = 0

    profile = {
        "column_name": column_name,
        "data_type": str(col.dtype),
        "missing_values": null_count,
        "missing_percentage": round(missing_percentage, 2),
        "unique_values": col.n_unique(),
        "summary_stats": col.describe().to_dicts()[0]
    }

    # Histogram for numeric columns
    if col.dtype in [pl.Int64, pl.Int32, pl.Int16, pl.Int8, pl.Float64, pl.Float32]:
        try:
            # Drop nulls and NaNs for histogram calculation
            valid_data = col.drop_nulls().drop_nans()
            if not valid_data.is_empty():
                hist = valid_data.hist(bin_count=20)
                # Extracting the data for plotly
                hist_data = {
                    "counts": hist.get_columns()[1].to_list(),
                    "bin_edges": hist.get_columns()[0].to_list()
                }
                profile["histogram"] = hist_data
        except Exception as e:
            # In case histogram fails for some reason
            print(f"Could not generate histogram for column {column_name}: {e}")


    # Specific analysis for String columns
    if col.dtype == pl.String:
        # Check for leading/trailing whitespace
        # Note: This can be slow on very large datasets.
        # A more performant approach for huge data might sample the data.
        has_whitespace = col.str.strip_chars() != col
        has_whitespace = has_whitespace.any() if not has_whitespace.is_empty() else False


        # Check for inconsistent capitalization
        # Heuristic: if lowercasing reduces the number of unique values, there are inconsistencies.
        if col.n_unique() > 0 and null_count < total_count:
             has_inconsistent_caps = col.drop_nulls().str.to_lowercase().n_unique() < col.drop_nulls().n_unique()
        else:
            has_inconsistent_caps = False

        profile["text_analysis"] = {
            "has_leading_trailing_whitespace": bool(has_whitespace),
            "has_inconsistent_capitalization": bool(has_inconsistent_caps)
        }

        # Date analysis for string columns using dateparser
        non_null_series = col.drop_nulls()
        if not non_null_series.is_empty():
            # Use a sample to avoid parsing the whole column, which can be slow.
            sample_size = min(len(non_null_series), 100)
            sample = non_null_series.sample(n=sample_size)

            parsed_dates = sample.map_elements(lambda s: dateparser.parse(s) is not None, return_dtype=pl.Boolean)

            num_parsed = parsed_dates.sum()

            # Heuristic: if > 50% of the sample parses as dates, treat it as a date column
            if num_parsed / sample_size > 0.5:
                # Now, let's count the total number of parse failures in the whole column
                # This is more expensive, so we only do it if we're confident it's a date column
                total_failures = col.map_elements(lambda s: dateparser.parse(s) is None, return_dtype=pl.Boolean).sum()

                profile["date_analysis"] = {
                    "is_potential_date_column": True,
                    "parse_failure_count": total_failures - col.null_count()
                }

    return profile

def profile_dataframe(df: pl.DataFrame) -> List[Dict[str, Any]]:
    """
    Generates a profile for each column in a Polars DataFrame.

    Args:
        df: The Polars DataFrame to profile.

    Returns:
        A list of dictionaries, where each dictionary is a profile for a column.
    """
    report = []
    for column_name in df.columns:
        report.append(get_column_profile(df, column_name))
    return report
