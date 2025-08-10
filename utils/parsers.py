import polars as pl
from pathlib import Path
from typing import Optional

def load_data(file_path: str, sheet_name: Optional[str] = None) -> pl.DataFrame:
    """
    Load data from a CSV or Excel file into a Polars DataFrame.

    Args:
        file_path: The path to the input file.
        sheet_name: The name of the sheet to read from an Excel file.
                    If None, the first sheet is read.

    Returns:
        A Polars DataFrame containing the loaded data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is not supported or if there's an issue loading the file.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Error: The file '{file_path}' was not found.")

    file_extension = path.suffix.lower()

    try:
        if file_extension == '.csv':
            return pl.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            return pl.read_excel(file_path, sheet_name=sheet_name)
        else:
            raise ValueError(f"Unsupported file format: '{file_extension}'. Please use a CSV or Excel file.")
    except Exception as e:
        raise ValueError(f"Failed to load the file '{file_path}'. Reason: {e}")
