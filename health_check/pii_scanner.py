import polars as pl
import re
from typing import List, Dict

# PII patterns
# A simple email regex
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
# A simple phone regex (covers many international formats)
PHONE_REGEX = re.compile(r"(\+\d{1,3}[-\s]?)?(\(?\d{3}\)?[-\s]?)?\d{3}[-\s]?\d{4}")
# More specific regex for Indian phone numbers
INDIAN_PHONE_REGEX = re.compile(r"(?:\+91)?[-\s]?[6-9]\d{9}")

PII_PATTERNS = {
    "Email": EMAIL_REGEX,
    "Phone": PHONE_REGEX,
    "Indian_Phone": INDIAN_PHONE_REGEX,
}

def scan_pii(df: pl.DataFrame, sample_size: int = 1000) -> Dict[str, List[str]]:
    """
    Scans a DataFrame for columns that may contain Personally Identifiable Information (PII).

    Args:
        df: The Polars DataFrame to scan.
        sample_size: The number of non-null rows to sample from each column for checking.

    Returns:
        A dictionary where keys are PII types (e.g., "Email") and values are lists of
        column names that are suspected of containing that type of PII.
    """
    pii_report = {pii_type: [] for pii_type in PII_PATTERNS.keys()}

    string_columns = [col for col in df.columns if df[col].dtype == pl.String]

    for col_name in string_columns:
        # Take a sample of the column to avoid slow checks on huge data
        sample = df[col_name].drop_nulls().head(sample_size)

        if sample.is_empty():
            continue

        for pii_type, pattern in PII_PATTERNS.items():
            # If the column has already been flagged for this PII type, skip
            if col_name in pii_report[pii_type]:
                continue

            # Check if any value in the sample matches the regex pattern
            if sample.str.contains(pattern.pattern).any():
                pii_report[pii_type].append(col_name)

    return pii_report
