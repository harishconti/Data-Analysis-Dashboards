# HOW TO USE

This guide provides a comprehensive overview of the Data Health Check Tool, including its features, usage instructions, and design rationale.

## Features

  * **Comprehensive Data Profiling**: Generates a detailed profile for each column, including data types, missing values, unique values, and summary statistics.
  * **Interactive Visualizations**: The HTML report includes interactive histograms for numeric columns, allowing for a deeper understanding of data distribution.
  * **Advanced Date Parsing**: Uses the `dateparser` library to automatically detect and validate a wide variety of date formats in string columns.
  * **Configurable PII Scanning**: Scans for Personally Identifiable Information using customizable regex patterns defined in the configuration file.
  * **Pluggable Scanner Architecture**: The tool is designed to be extensible. You can add new scanners by simply adding a new Python module to the `health_check/scanners` directory.
  * **AI-Powered Summaries (Optional)**: If configured, the tool can use the Gemini API to generate a high-level, natural language summary of the data's health.
  * **Flexible Configuration**: A `config.yaml` file allows you to customize the tool's behavior, from PII patterns to report titles and AI settings.
  * **Multiple Report Formats**: Generates both a quick console summary and a detailed, interactive HTML report to suit different needs.

## Installation

First, ensure you have Python installed. Then, install the required Python packages from the root of the project using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Configuration

The tool's behavior is controlled by the `config.yaml` file. This allows you to customize the analysis without changing the source code.

  * **`pii`**: Define custom regular expression patterns for the PII scanner. The key is the PII type name (e.g., `email`), and the value is the regex pattern.
    ```yaml
    pii:
      patterns:
        email: "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+"
        phone: "(\\+\\d{1,3}[-\\s]?)?(\\(?\\d{3}\\)?[-\\s]?)?\\d{3}[-\\s]?\\d{4}"
    ```
  * **`reporting`**: Control the report generation. You can enable or disable HTML and console reports, and set the title for the HTML report.
    ```yaml
    reporting:
      generate_html: true
      generate_console: true
      html_title: "Data Health Check Report"
    ```
  * **`gemini`**: Configure the optional AI-powered summary. To use this, you must enable it, provide a model name, and set the `GOOGLE_API_KEY` environment variable. You can also customize the prompt sent to the model.
    ```yaml
    gemini:
      enabled: false
      model: "gemini-pro"
      prompt: "Generate a summary of the data health check report..."
    ```

## How to Run the Analysis

To run a health check, use the `main.py` script located in the `health_check` directory.

### Basic Usage

This command runs the analysis on a data file with default settings, using the `config.yaml` from the project root.

```bash
python health_check/main.py path/to/your/data.csv
```

### Command-Line Options

You can override settings from the `config.yaml` file using the following command-line arguments:

| Option              | Alias | Description                                                                    |
| ------------------- | ----- | ------------------------------------------------------------------------------ |
| `--config`          | `-c`  | Path to a custom configuration file.                                         |
| `--sheet`           |       | The name of the Excel sheet to analyze. Defaults to the first sheet. |
| `--output`          | `-o`  | Filename for the output HTML report. Overrides the config file setting. |
| `--no-html`         |       | Disable the generation of the HTML report. Overrides the config file setting. |

### Example with Options

The following command analyzes the "Sales Data" sheet from an Excel file, uses a custom configuration, and saves the report with a specific name:

```bash
python health_check/main.py "data/my_data.xlsx" --config "configs/custom_config.yaml" --sheet "Sales Data" --output "sales_report.html"
```
