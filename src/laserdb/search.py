"""Search and filtering API."""

from __future__ import annotations

from typing import Any

import pandas as pd

from laserdb.constants import SORT_COLUMNS
from laserdb.filters import filter_by_country, filter_by_laser_type, filter_by_power, filter_by_wavelength

TEXT_COLUMNS = ["laser_name", "facility", "country", "facility_status", "doi_or_link"]


def _text_search(df: pd.DataFrame, query: str | None) -> pd.DataFrame:
    if not query:
        return df
    query_lower = query.lower()
    haystack = df[TEXT_COLUMNS].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
    return df[haystack.str.contains(query_lower, regex=False)]


def _range_filter(df: pd.DataFrame, column: str, bounds: tuple[Any, Any] | list[Any]) -> pd.DataFrame:
    low, high = bounds
    out = df
    if low is not None:
        out = out[out[column] >= low]
    if high is not None:
        out = out[out[column] <= high]
    return out


def search_lasers(
    df: pd.DataFrame,
    query: str | None = None,
    filters: dict[str, Any] | None = None,
    sort_by: str | None = None,
    ascending: bool | None = None,
) -> pd.DataFrame:
    """Search a processed laser DataFrame and return a filtered DataFrame."""
    out = _text_search(df, query)
    filters = filters or {}

    exact_columns = [
        "facility",
        "demonstrated_status",
        "facility_status_group",
        "wavelength_band",
    ]
    if "laser_type" in filters:
        out = filter_by_laser_type(out, filters["laser_type"])
    if "country" in filters:
        out = filter_by_country(out, filters["country"])
    for column in exact_columns:
        values = filters.get(column)
        if values:
            values = [values] if isinstance(values, str) else list(values)
            out = out[out[column].isin(values)]

    if "power_pw" in filters:
        out = filter_by_power(out, *filters["power_pw"])
    if "wavelength_nm" in filters:
        out = filter_by_wavelength(out, *filters["wavelength_nm"])

    range_map = {
        "peak_power_w": "peak_power_w_num",
        "wavelength_m": "wavelength_m_num",
        "wavelength_um": "wavelength_um",
        "rep_rate_hz": "rep_rate_hz_num",
        "max_intensity_w_m2": "max_intensity_w_m2_num",
        "max_intensity_w_cm2": "max_intensity_w_cm2",
        "pulse_energy_j": "pulse_energy_j_num",
        "pulse_duration_fs": "pulse_duration_fs_num",
        "pulse_duration_ps": "pulse_duration_ps",
        "year": "year_num",
    }
    for filter_name, column in range_map.items():
        if filter_name in filters:
            out = _range_filter(out, column, filters[filter_name])

    bool_columns = {
        "petawatt_class": "is_petawatt_class",
        "multipetawatt_class": "is_multipetawatt_class",
        "10pw_class": "is_10pw_class",
        "has_source": "has_source",
    }
    for filter_name, column in bool_columns.items():
        if filter_name in filters and filters[filter_name] is not None:
            out = out[out[column] == filters[filter_name]]
    if filters.get("complete_foms_only"):
        out = out[out["fom_completeness_score"] == 1]

    if sort_by:
        if sort_by in SORT_COLUMNS:
            column, default_ascending = SORT_COLUMNS[sort_by]
            out = out.sort_values(column, ascending=default_ascending if ascending is None else ascending)
        elif sort_by in out.columns:
            out = out.sort_values(sort_by, ascending=True if ascending is None else ascending)
    return out
