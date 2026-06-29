"""Reusable DataFrame filters."""

from __future__ import annotations

import pandas as pd


def _as_list(values) -> list:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    return list(values)


def filter_by_power(df: pd.DataFrame, min_pw: float | None = None, max_pw: float | None = None) -> pd.DataFrame:
    out = df
    if min_pw is not None:
        out = out[out["peak_power_pw"] >= min_pw]
    if max_pw is not None:
        out = out[out["peak_power_pw"] <= max_pw]
    return out


def filter_by_wavelength(
    df: pd.DataFrame, min_nm: float | None = None, max_nm: float | None = None
) -> pd.DataFrame:
    out = df
    if min_nm is not None:
        out = out[out["wavelength_nm"] >= min_nm]
    if max_nm is not None:
        out = out[out["wavelength_nm"] <= max_nm]
    return out


def filter_by_laser_type(df: pd.DataFrame, laser_types) -> pd.DataFrame:
    values = _as_list(laser_types)
    return df[df["laser_type"].isin(values)] if values else df


def filter_by_country(df: pd.DataFrame, countries) -> pd.DataFrame:
    values = _as_list(countries)
    return df[df["country"].isin(values)] if values else df


def filter_by_boolean(df: pd.DataFrame, column: str, value: bool | None) -> pd.DataFrame:
    if value is None:
        return df
    return df[df[column] == value]
