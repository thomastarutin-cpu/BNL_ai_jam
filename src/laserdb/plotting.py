"""Plotly plotting helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px


def peak_power_vs_duration(df: pd.DataFrame, log_power: bool = True):
    return px.scatter(
        df,
        x="pulse_duration_fs_num",
        y="peak_power_pw",
        color="laser_type",
        hover_name="laser_name",
        hover_data=["facility", "country", "year", "doi_or_link"],
        log_y=log_power,
        log_x=True,
        labels={"pulse_duration_fs_num": "Pulse duration (fs)", "peak_power_pw": "Peak power (PW)"},
    )


def peak_power_vs_rep_rate(df: pd.DataFrame, log_power: bool = True, log_rep_rate: bool = True):
    return px.scatter(
        df,
        x="rep_rate_hz",
        y="peak_power_pw",
        color="facility_status_group",
        hover_name="laser_name",
        hover_data=["facility", "country", "laser_type"],
        log_x=log_rep_rate,
        log_y=log_power,
        labels={"rep_rate_hz": "Repetition rate (Hz)", "peak_power_pw": "Peak power (PW)"},
    )


def wavelength_vs_peak_power(df: pd.DataFrame, log_power: bool = True, log_wavelength: bool = True):
    return px.scatter(
        df,
        x="wavelength_nm",
        y="peak_power_pw",
        color="laser_type",
        hover_name="laser_name",
        hover_data=["facility", "country"],
        log_x=log_wavelength,
        log_y=log_power,
        labels={"wavelength_nm": "Wavelength (nm)", "peak_power_pw": "Peak power (PW)"},
    )


def peak_power_histogram(df: pd.DataFrame):
    return px.histogram(df, x="peak_power_pw", nbins=30, labels={"peak_power_pw": "Peak power (PW)"})


def counts_by_country(df: pd.DataFrame):
    counts = df["country"].fillna("missing").replace("", "missing").value_counts().reset_index()
    counts.columns = ["country", "records"]
    return px.bar(counts, x="country", y="records", labels={"records": "Records"})


def counts_by_laser_type(df: pd.DataFrame):
    counts = df["laser_type"].fillna("missing").replace("", "missing").value_counts().reset_index()
    counts.columns = ["laser_type", "records"]
    return px.bar(counts, x="laser_type", y="records", labels={"records": "Records"})


def missingness_heatmap(df: pd.DataFrame):
    columns = [
        "peak_power_w_num",
        "wavelength_m_num",
        "rep_rate_hz_num",
        "max_intensity_w_m2_num",
        "pulse_energy_j_num",
        "pulse_duration_fs_num",
    ]
    matrix = df[columns].notna().astype(int)
    return px.imshow(
        matrix.T,
        aspect="auto",
        labels={"x": "Record index", "y": "FOM", "color": "Parsed"},
        y=columns,
        color_continuous_scale=["#d9dee7", "#2364aa"],
    )


def write_figures(df: pd.DataFrame, outdir: str | Path) -> None:
    path = Path(outdir)
    path.mkdir(parents=True, exist_ok=True)
    figures = {
        "peak_power_vs_duration.html": peak_power_vs_duration(df),
        "peak_power_vs_rep_rate.html": peak_power_vs_rep_rate(df),
        "wavelength_vs_peak_power.html": wavelength_vs_peak_power(df),
        "peak_power_histogram.html": peak_power_histogram(df),
        "counts_by_country.html": counts_by_country(df),
        "counts_by_laser_type.html": counts_by_laser_type(df),
        "missingness_heatmap.html": missingness_heatmap(df),
    }
    for filename, fig in figures.items():
        fig.write_html(path / filename)
