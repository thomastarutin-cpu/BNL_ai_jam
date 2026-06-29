"""Export helpers."""

import json
from pathlib import Path

import pandas as pd


def metadata_summary(df: pd.DataFrame) -> dict:
    return {
        "records": int(len(df)),
        "facilities": int(df["facility"].nunique(dropna=True)),
        "countries": int(df["country"].nunique(dropna=True)),
        "laser_type_codes": sorted([str(v) for v in df["laser_type"].dropna().unique()]),
        "petawatt_class_records": int(df["is_petawatt_class"].sum()),
        "records_with_sources": int(df["has_source"].sum()),
        "overall_fom_completeness": float(df["fom_completeness_score"].mean()),
    }


def write_metadata_summary(df: pd.DataFrame, path: str | Path) -> None:
    Path(path).write_text(json.dumps(metadata_summary(df), indent=2))
