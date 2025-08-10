# Data Health Check Tool

This tool is the first module of the Data Analysis Dashboards application. It is designed to perform a rapid, comprehensive, and automated quality assessment of tabular data files (CSV and Excel). The goal is to quickly identify common data quality issues, provide a clear summary of a dataset's health, and highlight potential risks like the presence of Personally Identifiable Information (PII).

This tool is perfect for the initial "discovery" phase of any data project, providing the essential insights needed to scope cleaning and transformation work.

## Features

* **Comprehensive Data Profiling**: Generates a detailed profile for each column in the dataset, including:
    * Inferred Data Type (`Integer`, `Float`, `String`, `Date`, etc.)
    * Percentage of Missing Values
    * Cardinality (Number of Unique Values)
    * Descriptive Statistics (mean, median, std dev, min, max for numeric columns)
* **Data Quality & Integrity Checks**: Automatically flags common issues such as:
    * Inconsistent text formatting (e.g., "Bengaluru", "bengaluru")
    * Leading or trailing whitespace
    * Mixed data types within a single column
    * Inconsistent date formats
* **PII (Personally Identifiable Information) Scanner**: Scans all text columns using regular expressions to identify and report the potential presence of:
    * Email Addresses
    * Phone Numbers
    * Other sensitive patterns
* **Flexible Output**: Generates a clean and easy-to-read report in multiple formats:
    * Console output for quick checks
    * Detailed HTML report for sharing with stakeholders

## How to Use

*(This section will be filled out as the tool is built)*

1.  **Installation**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Running the Check**:
    ```bash
    python health_check/main.py --file "path/to/your/data.csv"
    ```

temp structure

/data-analysis-dashboards
|
|-- .gitignore
|-- README.md           # The main project README you already have
|-- requirements.txt    # Your existing requirements file
|
|-- /health_check/      # <-- NEW: Directory for the Data Health Check tool
|   |-- __init__.py
|   |-- main.py         # <-- NEW: The main script to run the health check
|   |-- profiler.py     # <-- NEW: Module for data profiling logic
|   |-- pii_scanner.py  # <-- NEW: Module for PII scanning logic
|   |-- reporting.py    # <-- NEW: Module to generate HTML/console reports
|   |-- README.md       # <-- NEW: The detailed README for this specific tool (content above)
|
|-- /utils/             # <-- Your existing utils folder for shared code
|   |-- __init__.py
|   |-- parsers.py      # <-- NEW (Suggestion): Functions to handle CSV/Excel parsing
|
|-- /tests/             # <-- NEW (Suggestion): A dedicated folder for tests
|   |-- test_profiler.py
|   |-- test_pii_scanner.py
|   |-- test_data/      # Sample data for testing
|       |-- sample_with_pii.csv
|
|-- /temp/              # Folder for temporary files, ignored by git
|-- /venv/              # Virtual environment folder, ignored by git