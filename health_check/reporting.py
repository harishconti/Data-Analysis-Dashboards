import polars as pl
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.io as pio
from jinja2 import Environment, FileSystemLoader
import os
import google.generativeai as genai

def format_console_report(profile_report: List[Dict[str, Any]], pii_report: Dict[str, List[str]], file_path: str) -> str:
    """
    Formats the analysis results into a string for console output.
    """
    report_lines = []
    report_lines.append("="*50)
    report_lines.append(f"Data Health Check Report for: {file_path}")
    report_lines.append("="*50)
    report_lines.append("\n")

    # Column Profiles
    report_lines.append("--- Column Profiles ---")
    for profile in profile_report:
        report_lines.append("\n" + "-"*20)
        report_lines.append(f"Column: '{profile['column_name']}'")
        report_lines.append(f"  Data Type: {profile['data_type']}")
        report_lines.append(f"  Missing: {profile['missing_values']} ({profile['missing_percentage']}%)")
        report_lines.append(f"  Unique Values: {profile['unique_values']}")

        issues = []
        if "text_analysis" in profile:
            if profile["text_analysis"]["has_leading_trailing_whitespace"]:
                issues.append("Leading/Trailing Whitespace")
            if profile["text_analysis"]["has_inconsistent_capitalization"]:
                issues.append("Inconsistent Capitalization")

        if issues:
            report_lines.append(f"  Text Issues: {', '.join(issues)}")

        if "date_analysis" in profile:
            failures = profile["date_analysis"]["parse_failure_count"]
            report_lines.append(f"  Date Issues: Found {failures} values that could not be parsed as dates.")


    # PII Scan Results
    report_lines.append("\n\n" + "="*50)
    report_lines.append("--- PII Scan Results ---")
    pii_found = False
    for pii_type, columns in pii_report.items():
        if columns:
            pii_found = True
            report_lines.append(f"[WARNING] Found potential '{pii_type}' in columns: {', '.join(columns)}")

    if not pii_found:
        report_lines.append("[INFO] No common PII patterns were detected.")

    report_lines.append("="*50)
    return "\n".join(report_lines)

def generate_html_report(profile_report: List[Dict[str, Any]], pii_report: Dict[str, List[str]], file_path: str, output_filename: str, config: Dict[str, Any] = None):
    """
    Generates an interactive HTML report from the analysis results using Jinja2 and Plotly.
    """
    reporting_config = config.get("reporting", {}) if config else {}
    title = reporting_config.get("html_title", "Data Health Check Report")

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html.j2")

    # Generate plots for numeric columns
    for profile in profile_report:
        if "histogram" in profile:
            hist_data = profile["histogram"]

            # The histogram from polars gives bin edges, so we have one more edge than count.
            # We can represent this as a bar chart.
            fig = go.Figure(data=[go.Bar(
                x=hist_data["bin_edges"][:-1], # Left edges of bins
                y=hist_data["counts"],
                width=[(hist_data["bin_edges"][i+1] - hist_data["bin_edges"][i]) * 0.95 for i in range(len(hist_data["counts"]))] # Bar widths
            )])

            fig.update_layout(
                title_text=f"Distribution of {profile['column_name']}",
                xaxis_title="Value",
                yaxis_title="Frequency",
                bargap=0.05,
            )

            # Convert plot to HTML
            profile["plot"] = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')


    # Generate Gemini summary if enabled
    gemini_summary = generate_gemini_summary(profile_report, pii_report, config)

    # Render the template
    html_content = template.render(
        title=title,
        file_path=file_path,
        profile_report=profile_report,
        pii_report=pii_report,
        gemini_summary=gemini_summary
    )

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_gemini_summary(profile_report: List[Dict[str, Any]], pii_report: Dict[str, List[str]], config: Dict[str, Any]) -> str:
    """
    Generates a summary of the data health check report using the Gemini API.
    """
    gemini_config = config.get("gemini", {})
    if not gemini_config.get("enabled", False):
        return ""

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Gemini summary was enabled, but the GOOGLE_API_KEY environment variable is not set."

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel(gemini_config.get("model", "gemini-pro"))

        # Sanitize reports for the prompt
        # We don't need to send everything, just the key insights
        simplified_profile = [
            {k: v for k, v in profile.items() if k not in ["histogram", "summary_stats", "plot"]}
            for profile in profile_report
        ]

        prompt_template = gemini_config.get("prompt",
            "You are a data analyst. Based on the following data profile and PII scan results, "
            "provide a short, high-level summary of the data's health. "
            "Focus on the most critical issues found.\n\n"
            "Data Profile: {profile_report}\n\n"
            "PII Report: {pii_report}"
        )

        prompt = prompt_template.format(profile_report=simplified_profile, pii_report=pii_report)

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not generate Gemini summary. Reason: {e}"
