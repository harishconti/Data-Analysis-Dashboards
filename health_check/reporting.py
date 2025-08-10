import polars as pl
from typing import List, Dict, Any

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

def generate_html_report(profile_report: List[Dict[str, Any]], pii_report: Dict[str, List[str]], file_path: str, output_filename: str):
    """
    Generates a simple HTML report from the analysis results.
    """
    html = f"""
    <html>
    <head>
        <title>Data Health Check Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .pii-warning {{ background-color: #ffdddd; border-left: 6px solid #f44336; padding: 10px; margin-top: 20px; }}
            .pii-ok {{ background-color: #ddffdd; border-left: 6px solid #4CAF50; padding: 10px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>Data Health Check Report</h1>
        <p><strong>Source File:</strong> {file_path}</p>

        <h2>Column Profiles</h2>
        <table>
            <tr>
                <th>Column Name</th>
                <th>Data Type</th>
                <th>Missing (%)</th>
                <th>Unique Values</th>
                <th>Potential Issues</th>
            </tr>
    """

    for profile in profile_report:
        issues = []
        if "text_analysis" in profile:
            if profile["text_analysis"]["has_leading_trailing_whitespace"]:
                issues.append("Whitespace")
            if profile["text_analysis"]["has_inconsistent_capitalization"]:
                issues.append("Capitalization")

        if "date_analysis" in profile:
            failures = profile['date_analysis']['parse_failure_count']
            issues.append(f"Date Parse Errors ({failures})")

        html += f"""
            <tr>
                <td>{profile['column_name']}</td>
                <td>{profile['data_type']}</td>
                <td>{profile['missing_percentage']}%</td>
                <td>{profile['unique_values']}</td>
                <td>{', '.join(issues) if issues else 'None'}</td>
            </tr>
        """

    html += "</table>"

    html += "<h2>PII Scan Results</h2>"
    pii_found = any(columns for columns in pii_report.values())

    if pii_found:
        html += '<div class="pii-warning">'
        html += "<strong>Warning:</strong> Potential PII detected in the following columns:"
        html += "<ul>"
        for pii_type, columns in pii_report.items():
            if columns:
                html += f"<li><strong>{pii_type}:</strong> {', '.join(columns)}</li>"
        html += "</ul></div>"
    else:
        html += '<div class="pii-ok"><strong>OK:</strong> No common PII patterns were detected.</div>'

    html += """
    </body>
    </html>
    """

    with open(output_filename, 'w') as f:
        f.write(html)
