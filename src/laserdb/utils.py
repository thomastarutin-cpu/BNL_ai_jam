"""Shared parsing and display utilities."""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Any

import numpy as np
import pandas as pd

from laserdb.constants import MISSING_VALUE_TOKENS

_NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
_UNDERSCORE_EXP_RE = re.compile(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))[eE]_([0-9]+)$")


def is_missing_value(value: Any) -> bool:
    """Return True for project-level missing-value tokens."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except TypeError:
        pass
    if isinstance(value, str):
        cleaned = value.replace("\u00a0", " ").strip().lower()
        return cleaned in MISSING_VALUE_TOKENS
    return False


def _normalize_numeric_text(value: Any, column_name: str | None = None) -> str | None:
    if is_missing_value(value):
        return None
    text = unicodedata.normalize("NFKC", str(value)).replace("\u00a0", " ").strip()
    text = text.replace(",", "")
    if text.lower() in MISSING_VALUE_TOKENS:
        return None
    match = _UNDERSCORE_EXP_RE.fullmatch(text)
    if match and column_name == "wavelength_m":
        return f"{match.group(1)}e-{match.group(2)}"
    return text


def parse_numeric_value(value: Any, column_name: str | None = None) -> float:
    """Parse a numeric value safely, returning NaN when parsing is not defensible."""
    if is_missing_value(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    text = _normalize_numeric_text(value, column_name=column_name)
    if text is None or not _NUMERIC_RE.fullmatch(text):
        return np.nan
    try:
        return float(text)
    except ValueError:
        return np.nan


def format_numeric_value(value: Any, unit: str | None = None, precision: int = 3) -> str:
    """Format numeric values for display without changing stored values."""
    numeric = parse_numeric_value(value)
    if math.isnan(numeric):
        return "Not reported"
    abs_value = abs(numeric)
    if abs_value != 0 and (abs_value >= 1e5 or abs_value < 1e-3):
        rendered = f"{numeric:.{precision}e}"
    else:
        rendered = f"{numeric:.{precision}g}"
    return f"{rendered} {unit}" if unit else rendered


def safe_get(record: Any, key: str, default: Any = None) -> Any:
    """Safely read a mapping or pandas Series value."""
    try:
        value = record.get(key, default)
    except AttributeError:
        value = default
    if is_missing_value(value):
        return default
    return value
