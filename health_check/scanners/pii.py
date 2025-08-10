import polars as pl
import re
from typing import List, Dict, Any

def scan(df: pl.DataFrame, config: Dict[str, Any], sample_size: int = 1000) -> Dict[str, List[str]]:
    """
    Scans a DataFrame for columns that may contain Personally Identifiable Information (PII)
    based on patterns defined in the configuration.

    Args:
        df: The Polars DataFrame to scan.
        config: The configuration dictionary.
        sample_size: The number of non-null rows to sample from each column for checking.

    Returns:
        A dictionary where keys are PII types and values are lists of column names
        suspected of containing that type of PII.
    """
    pii_config = config.get("pii", {})
    patterns = pii_config.get("patterns", {})

    if not patterns:
        return {"pii_scan_results": "No PII patterns found in configuration."}

    pii_report = {pii_type: [] for pii_type in patterns.keys()}
    string_columns = [col for col in df.columns if df[col].dtype == pl.String]

    for col_name in string_columns:
        sample = df[col_name].drop_nulls().head(sample_size)
        if sample.is_empty():
            continue

        for pii_type, pattern_str in patterns.items():
            if col_name in pii_report[pii_type]:
                continue

            try:
                pattern = re.compile(pattern_str)
                if sample.str.contains(pattern.pattern).any():
                    pii_report[pii_type].append(col_name)
            except re.error as e:
                # Handle invalid regex patterns in config gracefully
                print(f"Warning: Invalid regex for PII type '{pii_type}': {e}")


    return pii_report
