"""Data cleaning and derived-column generation."""

from __future__ import annotations

import re
from hashlib import blake2b
from typing import Any

import pandas as pd

from laserdb.constants import (
    CORE_COMPLETENESS_COLUMNS,
    DEMONSTRATED_STATUS,
    DISPLAY_UNIT_COLUMNS,
    FOM_COLUMNS,
    FOM_NUMERIC_COLUMNS,
    LASER_TYPE_CODES,
)
from laserdb.utils import is_missing_value, parse_numeric_value


def is_missing_like(value: Any) -> bool:
    return is_missing_value(value)


def normalize_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize whitespace in string cells without changing numeric cells."""
    out = df.copy()
    for column in out.columns:
        out[column] = out[column].map(
            lambda value: re.sub(r"\s+", " ", value.replace("\u00a0", " ")).strip()
            if isinstance(value, str)
            else value
        )
    return out


def add_numeric_fom_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for raw_column, numeric_column in FOM_NUMERIC_COLUMNS.items():
        out[numeric_column] = out[raw_column].map(lambda value: parse_numeric_value(value, raw_column))
    out["year_num"] = out["year"].map(lambda value: parse_numeric_value(value, "year")).astype("Float64")
    return out


def add_display_unit_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for display_column, (source_column, factor) in DISPLAY_UNIT_COLUMNS.items():
        out[display_column] = out[source_column] * factor
    return out


def _slug_part(value: Any) -> str:
    if is_missing_like(value):
        return "unknown"
    text = str(value).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "unknown"


def make_record_id(row: pd.Series) -> str:
    base = "-".join(
        [_slug_part(row.get("laser_name")), _slug_part(row.get("facility")), _slug_part(row.get("year"))]
    )
    digest = blake2b(base.encode("utf-8"), digest_size=3).hexdigest()
    return f"{base}-{digest}"


def classify_source(value: Any) -> str:
    if is_missing_like(value):
        return "missing"
    text = str(value).strip().lower()
    if text.startswith("10.") or "doi.org/" in text:
        return "doi"
    if text.startswith(("http://", "https://", "www.")):
        return "url"
    return "other"


def classify_wavelength_band(value_m: float) -> str:
    if pd.isna(value_m) or value_m <= 0:
        return "unknown"
    nm = value_m * 1e9
    if nm < 0.1:
        return "hard_xray"
    if nm < 200:
        return "soft_xray_euv"
    if nm < 700:
        return "visible"
    if nm < 2500:
        return "near_ir"
    if nm < 25000:
        return "mid_ir"
    return "far_ir_thz"


def classify_facility_status(value: Any) -> str:
    if is_missing_like(value):
        return "unknown"
    text = str(value).lower()
    if "commission" in text or "experimental" in text:
        return "commissioning"
    if "construction" in text or "planned" in text or "proposal" in text:
        return "under_construction"
    if "histor" in text or "decommission" in text or "retired" in text:
        return "historical"
    if "demonstrated" in text and "operational" not in text:
        return "demonstrated_only"
    if "operational" in text or "user" in text:
        return "operational"
    return "unknown"


def _row_completeness(row: pd.Series, columns: list[str]) -> float:
    return float(sum(not is_missing_like(row.get(column)) for column in columns) / len(columns))


def add_derived_status_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["record_id"] = out.apply(make_record_id, axis=1)
    out["source_kind"] = out["doi_or_link"].map(classify_source)
    out["has_source"] = out["source_kind"] != "missing"
    out["is_petawatt_class"] = out["peak_power_w_num"] >= 1e15
    out["is_multipetawatt_class"] = out["peak_power_w_num"] >= 2e15
    out["is_10pw_class"] = out["peak_power_w_num"] >= 1e16
    out["wavelength_band"] = out["wavelength_m_num"].map(classify_wavelength_band)
    out["facility_status_group"] = out["facility_status"].map(classify_facility_status)
    out["laser_type_label"] = out["laser_type"].map(LASER_TYPE_CODES).fillna("Unrecognized")
    out["demonstrated_label"] = out["demonstrated_status"].map(DEMONSTRATED_STATUS).fillna("Unrecognized")
    out["completeness_score"] = out.apply(_row_completeness, axis=1, columns=CORE_COMPLETENESS_COLUMNS)
    numeric_columns = list(FOM_NUMERIC_COLUMNS.values())
    out["fom_completeness_score"] = out[numeric_columns].notna().sum(axis=1) / len(numeric_columns)
    out["fom_missing_count"] = len(FOM_COLUMNS) - out[numeric_columns].notna().sum(axis=1)
    return out


def build_processed_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build a processed table while preserving original source columns."""
    out = normalize_whitespace(df)
    out = add_numeric_fom_columns(out)
    out = add_display_unit_columns(out)
    out = add_derived_status_columns(out)
    return out
