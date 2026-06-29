"""Input/output helpers."""

from pathlib import Path

import pandas as pd

from laserdb.constants import REQUIRED_COLUMNS


def load_workbook(path: str | Path) -> dict[str, pd.DataFrame]:
    """Load all sheets from an Excel workbook without normalizing cell values."""
    workbook_path = Path(path)
    if not workbook_path.exists():
        raise FileNotFoundError(f"Workbook not found: {workbook_path}")
    return pd.read_excel(workbook_path, sheet_name=None, keep_default_na=False)


def load_laser_data(path: str | Path, sheet_name: str = "Combined_Team13") -> pd.DataFrame:
    """Load the canonical laser data sheet and verify required columns."""
    sheets = load_workbook(path)
    if sheet_name not in sheets:
        available = ", ".join(sheets)
        raise ValueError(f"Required sheet {sheet_name!r} not found. Available sheets: {available}")
    df = sheets[sheet_name].copy()
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Workbook is missing required columns: {missing}")
    return df


def save_processed(df: pd.DataFrame, outdir: str | Path) -> None:
    """Save processed CSV and parquet exports."""
    output_dir = Path(outdir)
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "laser_data_processed.csv", index=False)
    parquet_df = df.copy()
    for column in parquet_df.select_dtypes(include=["object"]).columns:
        parquet_df[column] = parquet_df[column].map(lambda value: "" if pd.isna(value) else str(value))
    parquet_df.to_parquet(output_dir / "laser_data_normalized.parquet", index=False)
