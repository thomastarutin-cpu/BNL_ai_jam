"""Command-line interface."""

from pathlib import Path

import pandas as pd
import typer

from laserdb.clean import build_processed_table
from laserdb.export import metadata_summary
from laserdb.io import load_laser_data, save_processed
from laserdb.plotting import write_figures
from laserdb.search import search_lasers
from laserdb.summaries import country_summary, facility_summary, write_summary_outputs
from laserdb.validate import write_validation_outputs

app = typer.Typer(help="Laser facility database command-line tools.")


@app.command()
def build(
    input: Path = typer.Option(Path("combined_team13_format.xlsx"), "--input"),
    outdir: Path = typer.Option(Path("data/processed"), "--outdir"),
    reports: Path = typer.Option(Path("data/reports"), "--reports"),
) -> None:
    """Build processed CSV/parquet exports and reports."""
    raw = load_laser_data(input)
    outdir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(outdir / "laser_data_raw.csv", index=False)
    processed = build_processed_table(raw)
    save_processed(processed, outdir)
    write_validation_outputs(processed, reports)
    write_summary_outputs(processed, reports)
    typer.echo(f"Built {len(processed)} records.")


@app.command()
def validate(
    input: Path = typer.Option(Path("combined_team13_format.xlsx"), "--input"),
    reports: Path = typer.Option(Path("data/reports"), "--reports"),
) -> None:
    """Validate the workbook and write report files."""
    processed = build_processed_table(load_laser_data(input))
    report = write_validation_outputs(processed, reports)
    typer.echo(f"Validation complete: {report['record_count']} records, {report['parse_failure_count']} parse failures.")


@app.command()
def search(
    query: str | None = typer.Option(None, "--query"),
    laser_type: list[str] | None = typer.Option(None, "--laser-type"),
    country: list[str] | None = typer.Option(None, "--country"),
    min_power_pw: float | None = typer.Option(None, "--min-power-pw"),
    max_power_pw: float | None = typer.Option(None, "--max-power-pw"),
    processed: Path = typer.Option(Path("data/processed/laser_data_processed.csv"), "--processed"),
) -> None:
    """Search the processed database and print a compact table."""
    df = pd.read_csv(processed)
    filters = {
        "laser_type": laser_type,
        "country": country,
        "power_pw": (min_power_pw, max_power_pw),
    }
    result = search_lasers(df, query=query, filters=filters, sort_by="peak_power_desc")
    columns = ["laser_name", "facility", "country", "laser_type", "peak_power_pw", "doi_or_link"]
    typer.echo(result[columns].to_string(index=False))


@app.command()
def summary(
    group_by: str = typer.Option("country", "--group-by", help="country or facility"),
    processed: Path = typer.Option(Path("data/processed/laser_data_processed.csv"), "--processed"),
) -> None:
    """Print country or facility summary tables."""
    df = pd.read_csv(processed)
    table = country_summary(df) if group_by == "country" else facility_summary(df)
    typer.echo(table.to_string(index=False))


@app.command()
def figures(
    outdir: Path = typer.Option(Path("figures"), "--outdir"),
    processed: Path = typer.Option(Path("data/processed/laser_data_processed.csv"), "--processed"),
) -> None:
    """Write interactive Plotly HTML figures."""
    df = pd.read_csv(processed)
    write_figures(df, outdir)
    typer.echo(f"Wrote figures to {outdir}")


@app.command()
def metadata(processed: Path = typer.Option(Path("data/processed/laser_data_processed.csv"), "--processed")) -> None:
    """Print a JSON-like metadata summary."""
    typer.echo(metadata_summary(pd.read_csv(processed)))


if __name__ == "__main__":
    app()
