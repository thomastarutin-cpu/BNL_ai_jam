"""Validation and report generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from laserdb.clean import is_missing_like, parse_numeric_value
from laserdb.constants import (
    DEMONSTRATED_STATUS,
    FOM_COLUMNS,
    FOM_NUMERIC_COLUMNS,
    LASER_TYPE_CODES,
    REQUIRED_COLUMNS,
)


def find_parse_failures(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for raw_column, numeric_column in FOM_NUMERIC_COLUMNS.items():
        for idx, raw_value in df[raw_column].items():
            parsed = df.at[idx, numeric_column] if numeric_column in df.columns else parse_numeric_value(raw_value)
            if not is_missing_like(raw_value) and pd.isna(parsed):
                rows.append(
                    {
                        "row_index": int(idx),
                        "laser_name": df.at[idx, "laser_name"] if "laser_name" in df.columns else "",
                        "column": raw_column,
                        "raw_value": raw_value,
                    }
                )
    return pd.DataFrame(rows, columns=["row_index", "laser_name", "column", "raw_value"])


def missingness_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in df.columns:
        missing = df[column].map(is_missing_like).sum()
        rows.append(
            {
                "column": column,
                "missing_count": int(missing),
                "missing_fraction": float(missing / len(df)) if len(df) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def _records_missing(df: pd.DataFrame, column: str) -> list[dict[str, Any]]:
    if column not in df.columns:
        return []
    mask = df[column].map(is_missing_like)
    fields = []
    for field in ["record_id", "laser_name", "facility", "country", column]:
        if field in df.columns and field not in fields:
            fields.append(field)
    return df.loc[mask, fields].to_dict(orient="records")


def potential_unit_outliers(df: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("peak_power_w_num", 1e6, 1e18),
        ("wavelength_m_num", 1e-12, 1e-2),
        ("rep_rate_hz_num", 0, 1e12),
        ("max_intensity_w_m2_num", 1e10, 1e35),
        ("pulse_energy_j_num", 0, 1e8),
        ("pulse_duration_fs_num", 0, 1e15),
    ]
    rows = []
    for column, low, high in checks:
        if column not in df.columns:
            continue
        mask = df[column].notna() & ((df[column] < low) | (df[column] > high))
        for _, row in df.loc[mask].iterrows():
            rows.append(
                {
                    "record_id": row.get("record_id", ""),
                    "laser_name": row.get("laser_name", ""),
                    "column": column,
                    "value": row.get(column),
                    "message": f"Value outside gentle review range [{low:g}, {high:g}]",
                }
            )
    return pd.DataFrame(rows)


def validate_database(df: pd.DataFrame) -> dict[str, Any]:
    missing_required = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    duplicate_record_ids: list[str] = []
    if "record_id" in df.columns:
        duplicate_record_ids = sorted(df.loc[df["record_id"].duplicated(), "record_id"].astype(str).unique())

    recognized_laser_types = set(LASER_TYPE_CODES)
    unrecognized_laser_types = sorted(
        {
            str(value)
            for value in df.get("laser_type", pd.Series(dtype=object)).dropna().unique()
            if not is_missing_like(value) and str(value) not in recognized_laser_types
        }
    )
    recognized_demo = set(DEMONSTRATED_STATUS)
    unrecognized_demo = sorted(
        {
            str(value)
            for value in df.get("demonstrated_status", pd.Series(dtype=object)).dropna().unique()
            if not is_missing_like(value) and str(value) not in recognized_demo
        }
    )

    parse_failures = find_parse_failures(df)
    missing_summary = missingness_summary(df)
    outliers = potential_unit_outliers(df)
    incomplete_fom = (
        df.loc[df.get("fom_completeness_score", pd.Series([1] * len(df))) < 1]
        .get(["record_id", "laser_name", "facility", "fom_completeness_score", "fom_missing_count"])
        .to_dict(orient="records")
    )

    return {
        "record_count": int(len(df)),
        "missing_required_columns": missing_required,
        "duplicate_record_ids": duplicate_record_ids,
        "unrecognized_laser_types": unrecognized_laser_types,
        "unrecognized_demonstrated_status": unrecognized_demo,
        "parse_failure_count": int(len(parse_failures)),
        "parse_failures": parse_failures.to_dict(orient="records"),
        "missing_source_count": int(df["doi_or_link"].map(is_missing_like).sum()) if "doi_or_link" in df else 0,
        "missing_sources": _records_missing(df, "doi_or_link"),
        "missing_name": _records_missing(df, "laser_name"),
        "missing_facility": _records_missing(df, "facility"),
        "missing_country": _records_missing(df, "country"),
        "fom_missingness_by_column": missing_summary[missing_summary["column"].isin(FOM_COLUMNS)].to_dict(
            orient="records"
        ),
        "incomplete_fom_records": incomplete_fom,
        "potential_unit_outliers": outliers.to_dict(orient="records"),
    }


def validation_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# LaserBase Validation Report",
        "",
        f"- Records: {report['record_count']}",
        f"- Missing required columns: {report['missing_required_columns'] or 'none'}",
        f"- Duplicate record IDs: {report['duplicate_record_ids'] or 'none'}",
        f"- Unrecognized laser type codes: {report['unrecognized_laser_types'] or 'none'}",
        f"- Unrecognized demonstrated-status flags: {report['unrecognized_demonstrated_status'] or 'none'}",
        f"- Numeric parse failures: {report['parse_failure_count']}",
        f"- Records missing source links: {report['missing_source_count']}",
        f"- Records with incomplete FOMs: {len(report['incomplete_fom_records'])}",
        f"- Potential unit outliers for review: {len(report['potential_unit_outliers'])}",
        "",
        "## Notes",
        "",
        "This report flags records for curation. It does not modify raw scientific values.",
        "Missing values are not zeros. Parsed numeric columns are derived only for search and plotting.",
    ]
    if report["parse_failures"]:
        lines.extend(["", "## Parse Failures", ""])
        for failure in report["parse_failures"]:
            lines.append(
                f"- Row {failure['row_index']}: `{failure['laser_name']}` column "
                f"`{failure['column']}` value `{failure['raw_value']}`"
            )
    if report["potential_unit_outliers"]:
        lines.extend(["", "## Potential Unit Outliers", ""])
        for item in report["potential_unit_outliers"]:
            lines.append(
                f"- `{item['laser_name']}` `{item['column']}` = `{item['value']}`: {item['message']}"
            )
    return "\n".join(lines) + "\n"


def write_validation_outputs(df: pd.DataFrame, reports_dir: str | Path) -> dict[str, Any]:
    output_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = validate_database(df)
    (output_dir / "validation_report.json").write_text(json.dumps(report, indent=2, default=str))
    (output_dir / "validation_report.md").write_text(validation_report_markdown(report))
    find_parse_failures(df).to_csv(output_dir / "parse_failures.csv", index=False)
    missingness_summary(df).to_csv(output_dir / "missingness_summary.csv", index=False)
    return report
