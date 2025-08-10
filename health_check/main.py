import typer
from pathlib import Path
from typing import Optional
import importlib
import pkgutil

from utils.parsers import load_data
from utils.config import load_config
from health_check.profiler import profile_dataframe
from health_check.reporting import format_console_report, generate_html_report
import health_check.scanners

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
    config_path: str = typer.Option(
        "config.yaml",
        "--config",
        "-c",
        help="Path to the configuration file.",
    ),
    sheet_name: Optional[str] = typer.Option(
        None,
        "--sheet",
        help="The name of the Excel sheet to analyze. Defaults to the first sheet.",
    ),
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Filename for the output HTML report. Overrides config.",
    ),
    no_html: bool = typer.Option(
        None,
        "--no-html",
        help="Disable the generation of the HTML report. Overrides config.",
    )
):
    """
    Analyzes a given data file, prints a summary to the console, and generates an HTML report.
    """
    # 1. Load Configuration
    try:
        config = load_config(config_path)
        typer.echo("✅ Configuration loaded successfully.")
    except FileNotFoundError:
        typer.secho(f"🔥 Error: Configuration file not found at '{config_path}'.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"🔥 Error loading configuration: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"🚀 Starting analysis for: {file_path}")

    # 2. Load Data
    try:
        df = load_data(str(file_path), sheet_name=sheet_name)
        typer.echo(f"✅ Data loaded successfully. Shape: {df.shape}")
    except (FileNotFoundError, ValueError) as e:
        typer.secho(f"🔥 Error loading data: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 3. Profile DataFrame
    typer.echo("📊 Profiling data...")
    profile_report = profile_dataframe(df)

    # 4. Run all scanners
    typer.echo("🔍 Running all available scanners...")
    scanner_reports = {}
    scanner_package = health_check.scanners
    for _, module_name, _ in pkgutil.iter_modules(scanner_package.__path__):
        try:
            module = importlib.import_module(f"{scanner_package.__name__}.{module_name}")
            if hasattr(module, "scan"):
                typer.echo(f"  -> Running scanner: {module_name}")
                report = module.scan(df, config)
                scanner_reports[module_name] = report
        except Exception as e:
            typer.secho(f"  -> Failed to run scanner {module_name}: {e}", fg=typer.colors.YELLOW)

    # For now, we assume the main PII report is from the 'pii' scanner.
    # This can be made more generic later.
    pii_report = scanner_reports.get("pii", {})

    # Determine reporting settings
    reporting_config = config.get("reporting", {})
    should_gen_html = reporting_config.get("generate_html", True)
    if no_html is not None:
        should_gen_html = not no_html # CLI overrides config

    output_file = output_path or reporting_config.get("output_filename", "health_check_report.html")


    # 5. Generate and print console report
    if reporting_config.get("generate_console", True):
        typer.echo("\n" + "="*50)
        typer.echo("📋 CONSOLE REPORT")
        console_output = format_console_report(profile_report, pii_report, str(file_path))
        typer.echo(console_output)

    # 6. Generate HTML report
    if should_gen_html:
        try:
            generate_html_report(profile_report, pii_report, str(file_path), str(output_file), config=config)
            typer.secho(f"\n🎉 HTML report generated successfully at: {output_file}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"\n🔥 Could not generate HTML report. Reason: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    else:
        typer.echo("\nℹ️ HTML report generation was skipped.")

    typer.echo("\n✨ Analysis complete.")


if __name__ == "__main__":
    app()
