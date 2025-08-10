# Data Health Check Tool

This tool is the first module of the Data Analysis Dashboards application. It is designed to perform a rapid, comprehensive, and automated quality assessment of tabular data files (CSV and Excel). The goal is to quickly identify common data quality issues, provide a clear summary of a dataset's health, and highlight potential risks like the presence of Personally Identifiable Information (PII).

This tool is perfect for the initial "discovery" phase of any data project, providing the essential insights needed to scope cleaning and transformation work.

## Features

*   **Comprehensive Data Profiling**: Generates a detailed profile for each column, including data types, missing values, unique values, and summary statistics.
*   **Interactive Visualizations**: The HTML report includes interactive histograms for numeric columns, allowing for a deeper understanding of data distribution.
*   **Advanced Date Parsing**: Uses the `dateparser` library to automatically detect and validate a wide variety of date formats.
*   **Configurable PII Scanning**: Scans for Personally Identifiable Information using regex patterns. You can easily add your own custom patterns via a configuration file.
*   **Pluggable Scanner Architecture**: The tool is designed to be extensible. You can add new scanners by simply adding a new file to the `scanners` directory.
*   **AI-Powered Summaries (Optional)**: If configured, the tool can use the Gemini API to generate a high-level summary of the data's health.
*   **Flexible Configuration**: A `config.yaml` file allows you to customize the tool's behavior, from PII patterns to report titles.
*   **Multiple Report Formats**: Generates both a quick console summary and a detailed, interactive HTML report.

## How to Use

### 1. Installation

First, install the required Python packages from the root of the project:

```bash
pip install -r requirements.txt
```

### 2. Configuration

The tool is controlled by a `config.yaml` file in the root of the project. A default file is provided. Here are the key sections:

*   **`pii`**: Define custom regex patterns for the PII scanner.
*   **`reporting`**: Control the output of the reports, including the HTML report title.
*   **`gemini`**: Enable and configure the optional AI-powered summary. To use this, you must set the `GOOGLE_API_KEY` environment variable.

### 3. Running the Check

To run a health check on a data file, use the `main.py` script from the `health_check` directory.

**Basic Usage:**

```bash
python health_check/main.py path/to/your/data.csv
```

This will use the default `config.yaml` and generate a report named `health_check_report.html`.

**Command-Line Options:**

You can override some of the configuration settings using command-line arguments:

*   `--config`: Specify a different configuration file.
*   `--sheet`: If using an Excel file, specify the sheet name.
*   `--output`: Set a custom name for the output HTML file.
*   `--no-html`: Disable the generation of the HTML report.

**Example with options:**

```bash
python health_check/main.py "data/my_data.xlsx" --sheet "Sales Data" --output "sales_report.html"
```

## Project Structure

```
/
|-- config.yaml             # Main configuration file
|-- requirements.txt
|-- health_check/
|   |-- main.py             # Main script to run the health check
|   |-- profiler.py         # Data profiling logic
|   |-- reporting.py        # Report generation logic
|   |-- README.md           # This file
|   |-- /scanners/          # Pluggable scanners
|       |-- pii.py          # The PII scanner
|-- /templates/
|   |-- report.html.j2      # Jinja2 template for the HTML report
|-- /utils/
|   |-- config.py           # Configuration loading utility
|   |-- parsers.py          # Data file parsing utility
```