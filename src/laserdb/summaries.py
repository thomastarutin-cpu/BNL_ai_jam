"""Summary tables."""

from pathlib import Path

import pandas as pd


def facility_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("facility", dropna=False)
        .agg(
            records=("record_id", "count"),
            countries=("country", lambda s: ", ".join(sorted({str(v) for v in s.dropna() if str(v)}))),
            petawatt_records=("is_petawatt_class", "sum"),
            fom_completeness=("fom_completeness_score", "mean"),
        )
        .reset_index()
        .sort_values(["records", "facility"], ascending=[False, True])
    )


def country_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("country", dropna=False)
        .agg(
            records=("record_id", "count"),
            facilities=("facility", "nunique"),
            petawatt_records=("is_petawatt_class", "sum"),
            source_coverage=("has_source", "mean"),
        )
        .reset_index()
        .sort_values(["records", "country"], ascending=[False, True])
    )


def write_summary_outputs(df: pd.DataFrame, reports_dir: str | Path) -> None:
    outdir = Path(reports_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    facility_summary(df).to_csv(outdir / "facility_summary.csv", index=False)
    country_summary(df).to_csv(outdir / "country_summary.csv", index=False)
