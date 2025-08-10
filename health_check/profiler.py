import polars as pl
from typing import List, Dict, Any

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

        # Date analysis for string columns
        non_null_series = col.drop_nulls()
        if not non_null_series.is_empty():
            try:
                common_formats = [
                    "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y", "%m-%d-%Y",
                    "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",
                ]

                parse_expr = pl.coalesce(
                    [col.str.strptime(pl.Datetime, fmt, strict=False) for fmt in common_formats]
                ).alias("converted")

                converted_series = df.select(parse_expr).get_column("converted")

                original_non_null_count = col.drop_nulls().len()
                converted_successfully_count = converted_series.drop_nulls().len()

                # Heuristic: if > 50% of non-null strings parse as dates, treat it as a date column
                if original_non_null_count > 0 and (converted_successfully_count / original_non_null_count) > 0.5:
                    total_parse_failures = original_non_null_count - converted_successfully_count
                    if total_parse_failures > 0:
                        profile["date_analysis"] = {
                            "is_potential_date_column": True,
                            "parse_failure_count": total_parse_failures
                        }
            except Exception:
                # If anything goes wrong during the complex parsing, just skip it.
                pass

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
