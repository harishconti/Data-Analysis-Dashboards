import typer
from pathlib import Path
from typing import Optional

# It's better to have a central __init__.py that imports these,
# but for this structure, direct imports are fine.
from utils.parsers import load_data
from health_check.profiler import profile_dataframe
from health_check.pii_scanner import scan_pii
from health_check.reporting import format_console_report, generate_html_report

app = typer.Typer(help="A command-line tool to run a health check on tabular data files.")

@app.command()
def analyze(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the CSV or Excel file to analyze.",
    ),
    sheet_name: Optional[str] = typer.Option(
        None,
        "--sheet",
        help="The name of the Excel sheet to analyze. Defaults to the first sheet.",
    ),
    output_path: Path = typer.Option(
        "health_check_report.html",
        "--output",
        "-o",
        help="Filename for the output HTML report.",
    ),
    no_html: bool = typer.Option(
        False,
        "--no-html",
        help="Disable the generation of the HTML report.",
    )
):
    """
    Analyzes a given data file, prints a summary to the console, and generates an HTML report.
    """
    typer.echo(f"🚀 Starting analysis for: {file_path}")

    # 1. Load Data
    try:
        df = load_data(str(file_path), sheet_name=sheet_name)
        typer.echo(f"✅ Data loaded successfully. Shape: {df.shape}")
    except (FileNotFoundError, ValueError) as e:
        typer.secho(f"🔥 Error loading data: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 2. Profile DataFrame
    typer.echo("📊 Profiling data...")
    profile_report = profile_dataframe(df)

    # 3. Scan for PII
    typer.echo("🔍 Scanning for PII...")
    pii_report = scan_pii(df)

    # 4. Generate and print console report
    typer.echo("\n" + "="*50)
    typer.echo("📋 CONSOLE REPORT")
    console_output = format_console_report(profile_report, pii_report, str(file_path))
    typer.echo(console_output)

    # 5. Generate HTML report
    if not no_html:
        try:
            generate_html_report(profile_report, pii_report, str(file_path), str(output_path))
            typer.secho(f"\n🎉 HTML report generated successfully at: {output_path}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"\n🔥 Could not generate HTML report. Reason: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    else:
        typer.echo("\nℹ️ HTML report generation was skipped as requested.")

    typer.echo("\n✨ Analysis complete.")


if __name__ == "__main__":
    app()
