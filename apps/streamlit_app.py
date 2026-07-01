"""Streamlit application for the laser facility database."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from laserdb.constants import FOM_NUMERIC_COLUMNS, LASER_TYPE_CODES
from laserdb.export import metadata_summary
from laserdb.search import search_lasers
from laserdb.utils import format_numeric_value, is_missing_value, parse_numeric_value, safe_get
from laserdb.validate import validate_database, validation_report_markdown

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "laser_data_processed.csv"
LASER_TYPE_KEY_PATH = ROOT / "laser_type_key.txt"
GITHUB_REPO_URL = "https://github.com/thomastarutin-cpu/BNL_ai_jam"

COMPACT_COLUMNS = [
    "laser_name",
    "facility",
    "country",
    "laser_type",
    "facility_status",
    "demonstrated_status",
    "peak_power_pw",
    "wavelength_nm",
    "rep_rate_hz",
    "pulse_energy_j_num",
    "pulse_duration_fs_num",
    "doi_or_link",
]

DISPLAY_UNITS = {
    "peak_power_w_num": "W",
    "peak_power_pw": "PW",
    "wavelength_m_num": "m",
    "wavelength_nm": "nm",
    "wavelength_um": "um",
    "rep_rate_hz_num": "Hz",
    "rep_rate_hz": "Hz",
    "max_intensity_w_m2_num": "W/m^2",
    "max_intensity_w_cm2": "W/cm^2",
    "pulse_energy_j_num": "J",
    "pulse_duration_fs_num": "fs",
    "pulse_duration_ps": "ps",
}

COLUMN_LABELS = {
    "laser_name": "Laser / system",
    "facility": "Facility / institution",
    "country": "Country",
    "laser_type": "Laser type",
    "facility_status": "Facility status",
    "facility_status_group": "Status group",
    "demonstrated_status": "Demonstrated",
    "doi_or_link": "Source",
    "peak_power_w_num": "Peak power (W)",
    "peak_power_pw": "Peak power (PW)",
    "wavelength_m_num": "Wavelength (m)",
    "wavelength_nm": "Wavelength (nm)",
    "wavelength_um": "Wavelength (um)",
    "rep_rate_hz_num": "Repetition rate (Hz)",
    "rep_rate_hz": "Repetition rate (Hz)",
    "max_intensity_w_m2_num": "Maximum intensity (W/m^2)",
    "max_intensity_w_cm2": "Maximum intensity (W/cm^2)",
    "pulse_energy_j_num": "Pulse energy (J)",
    "pulse_duration_fs_num": "Pulse duration (fs)",
    "pulse_duration_ps": "Pulse duration (ps)",
    "year": "Year",
    "year_num": "Year",
    "wavelength_band": "Wavelength band",
}

FOM_LABELS = {
    "peak_power_w": "Peak power",
    "wavelength_m": "Wavelength",
    "rep_rate_s_inv": "Repetition rate",
    "max_intensity_w_m2": "Maximum intensity",
    "pulse_energy_j": "Pulse energy",
    "pulse_duration_fs": "Pulse duration",
}

PLOT_VARIABLES = {
    "Peak power (W)": "peak_power_w_num",
    "Peak power (PW)": "peak_power_pw",
    "Wavelength (m)": "wavelength_m_num",
    "Wavelength (nm)": "wavelength_nm",
    "Wavelength (um)": "wavelength_um",
    "Repetition rate (Hz)": "rep_rate_hz",
    "Maximum intensity (W/m^2)": "max_intensity_w_m2_num",
    "Maximum intensity (W/cm^2)": "max_intensity_w_cm2",
    "Pulse energy (J)": "pulse_energy_j_num",
    "Pulse duration (fs)": "pulse_duration_fs_num",
    "Pulse duration (ps)": "pulse_duration_ps",
    "Year": "year_num",
}

CATEGORICAL_COLOR_OPTIONS = {
    "None": None,
    "Laser type": "laser_type",
    "Country": "country",
    "Facility": "facility",
    "Status": "facility_status_group",
    "Demonstrated status": "demonstrated_status",
    "Wavelength band": "wavelength_band",
    "Year": "year_display",
}


@st.cache_data
def load_laser_type_key(path: Path) -> tuple[pd.DataFrame, str]:
    if not path.exists():
        fallback = pd.DataFrame(
            [{"Code": code, "Meaning": meaning, "Notes": ""} for code, meaning in LASER_TYPE_CODES.items()]
        )
        return fallback, ""
    text = path.read_text()
    records = []
    current: dict[str, str] | None = None
    notes: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if " = " in line:
            left, right = line.split(" = ", 1)
            code = left.strip()
            if code.isupper() and code.replace("_", "").isalpha() and len(code) <= 8:
                if current:
                    current["Notes"] = " ".join(notes).strip()
                    records.append(current)
                current = {"Code": code, "Meaning": right.strip(), "Notes": ""}
                notes = []
                continue
        if current:
            notes.append(line)
    if current:
        current["Notes"] = " ".join(notes).strip()
        records.append(current)
    table = pd.DataFrame(records) if records else pd.DataFrame(columns=["Code", "Meaning", "Notes"])
    return table, text


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year_display"] = df["year"].map(lambda value: "Not reported" if is_missing_value(value) else str(value))
    return df


def apply_app_css() -> None:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] .site-title {
            display: flex;
            align-items: center;
            gap: 0.72rem;
            color: inherit;
            font-size: 1.72rem;
            font-weight: 800;
            line-height: 1.2;
            letter-spacing: 0;
            padding: 0.35rem 0 1.1rem 0;
            text-decoration: none;
        }
        section[data-testid="stSidebar"] .site-title:hover {
            color: inherit;
            text-decoration: none;
        }
        section[data-testid="stSidebar"] .laserbase-mark {
            position: relative;
            display: inline-block;
            width: 2.9rem;
            height: 1.75rem;
            flex: 0 0 auto;
        }
        section[data-testid="stSidebar"] .laserbase-beam {
            position: absolute;
            left: 0;
            top: 0.86rem;
            width: 2.0rem;
            height: 0.16rem;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(35, 100, 170, 0) 0%, #2364aa 30%, #36c2ff 100%);
            box-shadow: 0 0 6px rgba(54, 194, 255, 0.75);
        }
        section[data-testid="stSidebar"] .laserbase-target {
            position: absolute;
            left: 1.94rem;
            top: 0.36rem;
            width: 0.34rem;
            height: 1.08rem;
            border-radius: 0.1rem;
            background: linear-gradient(180deg, #3c4657, #232b38);
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
        }
        section[data-testid="stSidebar"] .laserbase-flare {
            position: absolute;
            left: 1.70rem;
            top: 0.49rem;
            width: 0.82rem;
            height: 0.82rem;
            border-radius: 999px;
            background: radial-gradient(circle, #ffffff 0 12%, #ffd166 26%, #ff8a00 44%, rgba(255, 138, 0, 0) 70%);
            box-shadow: 0 0 8px rgba(255, 180, 60, 0.85);
        }
        .laserbase-hero {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 0.2rem 0 1rem 0;
        }
        .laserbase-hero .laserbase-mark {
            position: relative;
            display: inline-block;
            width: 4.4rem;
            height: 2.4rem;
            flex: 0 0 auto;
        }
        .laserbase-hero .laserbase-beam {
            position: absolute;
            left: 0;
            top: 1.16rem;
            width: 3.0rem;
            height: 0.22rem;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(35, 100, 170, 0) 0%, #2364aa 28%, #36c2ff 100%);
            box-shadow: 0 0 10px rgba(54, 194, 255, 0.8);
        }
        .laserbase-hero .laserbase-target {
            position: absolute;
            left: 2.86rem;
            top: 0.44rem;
            width: 0.46rem;
            height: 1.54rem;
            border-radius: 0.12rem;
            background: linear-gradient(180deg, #3c4657, #232b38);
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
        }
        .laserbase-hero .laserbase-flare {
            position: absolute;
            left: 2.45rem;
            top: 0.57rem;
            width: 1.28rem;
            height: 1.28rem;
            border-radius: 999px;
            background: radial-gradient(circle, #ffffff 0 12%, #ffd166 26%, #ff8a00 44%, rgba(255, 138, 0, 0) 72%);
            box-shadow: 0 0 14px rgba(255, 180, 60, 0.85);
        }
        .laserbase-hero-title {
            font-size: 3.2rem;
            font-weight: 800;
            line-height: 1;
            letter-spacing: 0;
        }
        .laserbase-hero-subtitle {
            color: #5d6472;
            font-size: 1.02rem;
            margin-top: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_navigation() -> str:
    home = "Overview"
    sections = ["Search", "Record Detail", "Plots", "Export", "Database Keys", "Contribute", "About"]
    valid_sections = [home, *sections]
    requested = st.query_params.get("section", home)
    if requested in valid_sections and st.session_state.get("section") != requested:
        st.session_state.section = requested
    if "section" not in st.session_state:
        st.session_state.section = home
    current = st.session_state.section
    if current not in valid_sections:
        current = home
        st.session_state.section = current
    st.sidebar.markdown(
        """
        <a class="site-title" href="?section=Overview" target="_self" aria-label="LaserBase home">
          <span class="laserbase-mark" aria-hidden="true">
            <span class="laserbase-beam"></span>
            <span class="laserbase-target"></span>
            <span class="laserbase-flare"></span>
          </span>
          <span>LaserBase</span>
        </a>
        """,
        unsafe_allow_html=True,
    )
    for section in sections:
        if st.sidebar.button(
            section,
            key=f"nav_{section}",
            use_container_width=True,
            type="primary" if section == current else "secondary",
        ):
            st.session_state.section = section
            st.query_params["section"] = section
            st.rerun()
    return current


def data_range(series: pd.Series) -> tuple[float, float]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return (0.0, 0.0)
    low = float(values.min())
    high = float(values.max())
    if low == high:
        high = low + 1.0
    return (low, high)


def format_filter_value(value: float) -> str:
    abs_value = abs(value)
    if abs_value != 0 and (abs_value >= 1e5 or abs_value < 1e-3):
        return f"{value:.6e}"
    return f"{value:.6g}"


def parse_filter_bound(value: str, label: str, bound: str) -> float | None:
    if is_missing_value(value):
        return None
    parsed = parse_numeric_value(value)
    if pd.isna(parsed):
        st.warning(f"{label}: {bound} value `{value}` is not a valid number.")
        return None
    return float(parsed)


def numeric_range_inputs(label: str, unit: str, series: pd.Series, key: str) -> tuple[float | None, float | None]:
    low, high = data_range(series)
    st.markdown(f"**{label} ({unit})**")
    cols = st.columns(2)
    min_text = cols[0].text_input(
        "Min",
        value=format_filter_value(low),
        key=f"{key}_min",
        help=f"Minimum {label.lower()} in {unit}. Scientific notation such as 2e8 is supported.",
    )
    max_text = cols[1].text_input(
        "Max",
        value=format_filter_value(high),
        key=f"{key}_max",
        help=f"Maximum {label.lower()} in {unit}. Scientific notation such as 2e8 is supported.",
    )
    min_value = parse_filter_bound(min_text, label, "minimum")
    max_value = parse_filter_bound(max_text, label, "maximum")
    if min_value is not None and max_value is not None and min_value > max_value:
        st.warning(f"{label}: minimum is greater than maximum.")
    return min_value, max_value


def display_text(value, default: str = "Not reported") -> str:
    if is_missing_value(value):
        return default
    return str(value)


def format_table_for_display(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.loc[:, [column for column in columns if column in df.columns]].copy()
    for column in out.columns:
        if column in DISPLAY_UNITS:
            out[column] = out[column].map(lambda value: format_numeric_value(value, DISPLAY_UNITS[column]))
        elif pd.api.types.is_numeric_dtype(out[column]):
            out[column] = out[column].map(format_numeric_value)
        else:
            out[column] = out[column].map(display_text)
    return out.rename(columns={column: COLUMN_LABELS.get(column, column) for column in out.columns})


def overview(df: pd.DataFrame) -> None:
    summary = metadata_summary(df)
    st.markdown(
        """
        <div class="laserbase-hero">
          <span class="laserbase-mark" aria-hidden="true">
            <span class="laserbase-beam"></span>
            <span class="laserbase-target"></span>
            <span class="laserbase-flare"></span>
          </span>
          <div>
            <div class="laserbase-hero-title">LaserBase</div>
            <div class="laserbase-hero-subtitle">
              A searchable catalogue of high-power lasers and related user facilities.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        LaserBase is a database effort for organizing source-backed information on high-power
        lasers and related user facilities. The database is designed to help researchers compare
        facility capabilities, find representative operating parameters, and maintain records on
        instruments worldwide.

        This project is presented as a part of the inaugural 2026 Brookhaven National Lab AI Jam,
        where it was awarded 1st place (see more in About).
        """
    )
    cols = st.columns(4)
    metrics = [
        ("Records", summary["records"]),
        ("Facilities", summary["facilities"]),
        ("Countries", summary["countries"]),
        ("Petawatt-class", summary["petawatt_class_records"]),
    ]
    for index, (label, value) in enumerate(metrics):
        cols[index % 4].metric(label, value)

    country_counts = (
        df["country"]
        .dropna()
        .astype(str)
        .loc[lambda series: series.str.strip().ne("")]
        .value_counts()
        .rename_axis("country")
        .reset_index(name="records")
    )
    if not country_counts.empty:
        st.subheader("Countries Represented")
        fig = px.choropleth(
            country_counts,
            locations="country",
            locationmode="country names",
            color="records",
            hover_name="country",
            color_continuous_scale=["#172033", "#1f4f8f", "#36c2ff", "#ffd166"],
            labels={"records": "Records"},
            template="plotly_dark",
        )
        fig.update_geos(
            bgcolor="#0b1020",
            landcolor="#172033",
            lakecolor="#0b1020",
            oceancolor="#0b1020",
            countrycolor="#354158",
            coastlinecolor="#354158",
            showframe=False,
            showocean=True,
            showlakes=True,
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="#0b1020",
            plot_bgcolor="#0b1020",
            coloraxis_colorbar_title="Records",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("How To Use The Website")
    st.markdown(
        """
        - Use **Search** to find facilities by name, country, laser type, status, wavelength band, or FOM range.
        - Use **Record Detail** to inspect one entry, including source values and display values for each FOM.
        - Use **Plots** to compare any two numeric FOMs and optionally color by facility metadata or a third FOM.
        - Use **Export** to download either the filtered table or the full processed database.
        - Use **Database Keys** to look up laser type codes and the acronyms used throughout the database.

        Missing or unavailable values are shown as `Not reported`. They are omitted from plots when the selected
        axis, legend, or color variable depends on that value.
        """
    )

    st.subheader("What The Database Contains")
    st.markdown(
        """
        Records may describe a facility, a beamline, a specific laser system, or a representative operating mode.
        Figure-of-merit values come from heterogeneous publications, facility pages, reports, and other source
        material. Source values are preserved, and missing values are treated as unavailable, not zero.
        """
    )


def render_laser_type_key() -> None:
    key_table, raw_text = load_laser_type_key(LASER_TYPE_KEY_PATH)
    st.subheader("Laser Type Key")
    if key_table.empty:
        st.info("Laser type key is not available.")
        return
    st.dataframe(key_table, use_container_width=True, hide_index=True)
    if raw_text:
        with st.expander("Full laser type notes"):
            st.markdown(raw_text)


def search_page(df: pd.DataFrame) -> pd.DataFrame:
    st.header("Search")
    with st.expander("Laser type key"):
        key_table, _ = load_laser_type_key(LASER_TYPE_KEY_PATH)
        st.dataframe(key_table, use_container_width=True, hide_index=True)
    query = st.text_input("Search", placeholder="Laser, facility, country, status, or source")
    cols = st.columns(3)
    countries = cols[0].multiselect("Country", sorted(df["country"].dropna().astype(str).unique()))
    types = cols[1].multiselect("Laser type", sorted(df["laser_type"].dropna().astype(str).unique()))
    status_groups = cols[2].multiselect(
        "Facility status", sorted(df["facility_status_group"].dropna().astype(str).unique())
    )
    cols = st.columns(3)
    demo = cols[0].multiselect(
        "Demonstrated status", sorted(df["demonstrated_status"].dropna().astype(str).unique())
    )
    bands = cols[1].multiselect("Wavelength band", sorted(df["wavelength_band"].dropna().astype(str).unique()))
    complete_only = cols[2].checkbox("Complete FOMs only")

    st.subheader("Numerical Filters")
    range_cols = st.columns(2)
    with range_cols[0]:
        peak_range = numeric_range_inputs("Peak power", "PW", df["peak_power_pw"], "peak_power_pw")
        rep_range = numeric_range_inputs("Repetition rate", "Hz", df["rep_rate_hz"], "rep_rate_hz")
    with range_cols[1]:
        wavelength_range = numeric_range_inputs("Wavelength", "nm", df["wavelength_nm"], "wavelength_nm")
        duration_range = numeric_range_inputs(
            "Pulse duration", "fs", df["pulse_duration_fs_num"], "pulse_duration_fs"
        )
    sort_by = st.selectbox(
        "Sort",
        [
            "peak_power_desc",
            "rep_rate_desc",
            "pulse_energy_desc",
            "pulse_duration_asc",
            "year_desc",
            "country",
            "facility",
            "name",
        ],
    )
    compact = st.toggle("Compact columns", value=True)

    filtered = search_lasers(
        df,
        query=query,
        filters={
            "country": countries,
            "laser_type": types,
            "facility_status_group": status_groups,
            "demonstrated_status": demo,
            "wavelength_band": bands,
            "power_pw": peak_range,
            "wavelength_nm": wavelength_range,
            "rep_rate_hz": rep_range,
            "pulse_duration_fs": duration_range,
            "complete_foms_only": complete_only,
        },
        sort_by=sort_by,
    )
    st.caption(f"{len(filtered)} records")
    shown_columns = COMPACT_COLUMNS if compact else list(filtered.columns)
    st.dataframe(format_table_for_display(filtered, shown_columns), use_container_width=True, hide_index=True)
    return filtered


def detail_page(df: pd.DataFrame) -> None:
    st.header("Record Detail")
    if df.empty or "record_id" not in df.columns:
        st.info("No records available.")
        return
    options = df["record_id"].dropna().astype(str).tolist()
    if not options:
        st.info("No selectable records available.")
        return
    labels = {
        str(row.record_id): f"{display_text(row.laser_name)} | {display_text(row.facility)} | {display_text(row.year)}"
        for row in df.itertuples()
    }
    selected = st.selectbox("Select record", options, format_func=lambda value: labels.get(value, value))
    selected_rows = df[df["record_id"].astype(str) == selected]
    if selected_rows.empty:
        st.info("Selected record is no longer available.")
        return
    row = selected_rows.iloc[0]

    st.subheader(display_text(safe_get(row, "laser_name")))
    cols = st.columns(3)
    cols[0].metric("Facility", display_text(safe_get(row, "facility")))
    cols[1].metric("Country", display_text(safe_get(row, "country")))
    cols[2].metric("Year", display_text(safe_get(row, "year")))

    laser_type = display_text(safe_get(row, "laser_type"))
    st.write(
        {
            "laser_type": f"{laser_type} - {LASER_TYPE_CODES.get(laser_type, 'Unrecognized')}",
            "facility_status": display_text(safe_get(row, "facility_status")),
            "demonstrated_status": display_text(safe_get(row, "demonstrated_status")),
            "source": display_text(safe_get(row, "doi_or_link")),
        }
    )

    fom_rows = []
    for raw_column, numeric_column in FOM_NUMERIC_COLUMNS.items():
        numeric_value = safe_get(row, numeric_column)
        unit = DISPLAY_UNITS.get(numeric_column)
        fom_rows.append(
            {
                "Figure of merit": f"{FOM_LABELS.get(raw_column, raw_column)} ({unit})",
                "Source value": display_text(safe_get(row, raw_column)),
                "Parsed display value": format_numeric_value(numeric_value, unit),
            }
        )
    st.dataframe(pd.DataFrame(fom_rows), use_container_width=True, hide_index=True)


def render_plot(
    df: pd.DataFrame,
    x_label: str,
    y_label: str,
    color_mode: str,
    color_label: str,
    log_x: bool,
    log_y: bool,
) -> None:
    color_column = (
        CATEGORICAL_COLOR_OPTIONS[color_label]
        if color_mode == "Categorical"
        else PLOT_VARIABLES[color_label]
    )
    x_column = PLOT_VARIABLES[x_label]
    y_column = PLOT_VARIABLES[y_label]

    plot_df = df.copy()
    for column in {x_column, y_column} | ({color_column} if color_mode == "Continuous FOM" and color_column else set()):
        plot_df[column] = pd.to_numeric(plot_df[column], errors="coerce")
    valid_mask = plot_df[x_column].notna() & plot_df[y_column].notna()
    if log_x:
        valid_mask &= plot_df[x_column] > 0
    if log_y:
        valid_mask &= plot_df[y_column] > 0
    if color_mode == "Continuous FOM" and color_column:
        valid_mask &= plot_df[color_column].notna()
    if color_mode == "Categorical" and color_column:
        valid_mask &= ~plot_df[color_column].map(is_missing_value)
        plot_df[color_column] = plot_df[color_column].map(display_text)

    omitted = int((~valid_mask).sum())
    plotted = plot_df.loc[valid_mask].copy()
    st.caption(
        f"Plotted {len(plotted)} records. Omitted {omitted} records with missing, "
        "invalid, or nonpositive log-scale values."
    )
    if plotted.empty:
        st.info("No records match the selected plotting variables.")
        return

    labels = {
        x_column: x_label,
        y_column: y_label,
    }
    if color_column:
        labels[color_column] = color_label

    fig = px.scatter(
        plotted,
        x=x_column,
        y=y_column,
        color=color_column,
        hover_name="laser_name",
        hover_data=["facility", "country", "laser_type", "year"],
        labels=labels,
        log_x=log_x,
        log_y=log_y,
        color_continuous_scale="Viridis" if color_mode == "Continuous FOM" else None,
    )
    fig.update_xaxes(exponentformat="e", showexponent="all")
    fig.update_yaxes(exponentformat="e", showexponent="all")
    fig.update_layout(margin=dict(l=0, r=0, t=12, b=0), height=620)
    st.plotly_chart(fig, use_container_width=True)


def plots_page(df: pd.DataFrame) -> None:
    st.header("Plots")
    st.caption(
        "Records with unavailable, invalid, or nonpositive log-scale values are omitted from the plot."
    )
    plot_variable_labels = list(PLOT_VARIABLES)
    category_labels = list(CATEGORICAL_COLOR_OPTIONS)

    x_label = st.session_state.get("plot_x_axis", plot_variable_labels[2])
    y_label = st.session_state.get("plot_y_axis", plot_variable_labels[1])
    color_mode = st.session_state.get("plot_color_mode", "Categorical")
    log_x = st.session_state.get("plot_log_x", True)
    log_y = st.session_state.get("plot_log_y", True)
    if color_mode == "Categorical":
        color_label = st.session_state.get("plot_category_color", category_labels[0])
    else:
        color_label = st.session_state.get("plot_fom_color", plot_variable_labels[5])

    render_plot(df, x_label, y_label, color_mode, color_label, log_x, log_y)

    with st.expander("Plot controls", expanded=True):
        controls = st.columns(3)
        controls[0].selectbox("X-axis", plot_variable_labels, index=plot_variable_labels.index(x_label), key="plot_x_axis")
        controls[1].selectbox("Y-axis", plot_variable_labels, index=plot_variable_labels.index(y_label), key="plot_y_axis")
        controls[2].selectbox("Color mode", ["Categorical", "Continuous FOM"], key="plot_color_mode")

        controls = st.columns(3)
        controls[0].checkbox("Log x-axis", value=log_x, key="plot_log_x")
        controls[1].checkbox("Log y-axis", value=log_y, key="plot_log_y")
        if color_mode == "Categorical":
            controls[2].selectbox(
                "Legend/category",
                category_labels,
                index=category_labels.index(color_label) if color_label in category_labels else 0,
                key="plot_category_color",
            )
        else:
            controls[2].selectbox(
                "Color variable",
                plot_variable_labels,
                index=plot_variable_labels.index(color_label) if color_label in plot_variable_labels else 5,
                key="plot_fom_color",
            )


def export_page(df: pd.DataFrame, filtered: pd.DataFrame) -> None:
    st.header("Export")
    st.download_button("Filtered CSV", filtered.to_csv(index=False), file_name="laser_data_filtered.csv")
    st.download_button("Full processed CSV", df.to_csv(index=False), file_name="laser_data_processed.csv")
    st.download_button(
        "JSON metadata summary",
        json.dumps(metadata_summary(df), indent=2),
        file_name="laser_database_metadata.json",
    )
    report = validation_report_markdown(validate_database(df))
    st.download_button("Validation report markdown", report, file_name="validation_report.md")


def database_keys_page() -> None:
    st.header("Database Keys")
    st.markdown(
        """
        This page collects the keys and abbreviations used throughout LaserBase. Use it as a
        reference when reading records, filtering the catalogue, or interpreting plots.
        """
    )

    render_laser_type_key()

    st.subheader("Abbreviations And Units")
    acronyms = pd.DataFrame(
        [
            ("FOM", "Figure of merit — a headline performance parameter such as peak power or pulse energy."),
            ("DOI", "Digital Object Identifier — a persistent link to the source publication or record."),
            ("PW", "Petawatt (10^15 watts) — unit used for peak power."),
            ("W", "Watt — unit used for peak power."),
            ("nm", "Nanometre (10^-9 m) — unit used for wavelength."),
            ("um", "Micrometre (10^-6 m) — unit used for wavelength."),
            ("m", "Metre — SI unit used for wavelength."),
            ("Hz", "Hertz — pulses (or shots) per second, used for repetition rate."),
            ("J", "Joule — unit used for pulse energy."),
            ("fs", "Femtosecond (10^-15 s) — unit used for pulse duration."),
            ("ps", "Picosecond (10^-12 s) — unit used for pulse duration."),
            ("W/cm^2", "Watts per square centimetre — unit used for maximum on-target intensity."),
            ("W/m^2", "Watts per square metre — SI unit used for maximum on-target intensity."),
            ("FEL", "Free-electron laser."),
            ("CPA", "Chirped pulse amplification."),
            ("OPCPA", "Optical parametric chirped pulse amplification."),
        ],
        columns=["Abbreviation", "Meaning"],
    )
    st.dataframe(acronyms, use_container_width=True, hide_index=True)

    st.subheader("Record Notes")
    st.markdown(
        """
        - Missing or unavailable values are shown as `Not reported` and are treated as unavailable, not zero.
        - Source values are preserved as reported; parsed display values are provided for comparison and plotting.
        - A record may represent a facility, a beamline, a specific laser system, or a representative operating mode.
        """
    )


def about_page() -> None:
    st.header("About")
    st.markdown(
        """
        This project was conducted as part of the Brookhaven National Laboratory (BNL) 2026 AI Jam.
        The goal of the competition was to use AI tools, namely OpenAI's ChatGPT and Codex, to
        work on novel projects as a way of demonstrating how these tools can be applied in
        scientific research. A total of 45 teams representing over 250 interns at BNL were each
        given a different task or question to address using the provided models. Teams worked on
        their projects from 9:00am to 3:30pm with guidance from a BNL faculty mentor. After the
        work period, a set of finalists were selected to give a brief presentation on their team's
        results, and three top prizes were named at the end.

        The LaserBase project, presented by Team 13, was awarded first prize. Although only Team 13
        was officially recognized with the top prize, the final product is the combined effort of
        Teams 11, 12, 13, 14, and 15. The data reported here represents the collective work gathered
        by all five groups, with the final database interface coming from Team 13's project.

        AI tools were used to conduct a large literature search, build the final user interface, and
        combine the five original datasets. All sources and entries in LaserBase were verified by
        hand, without the use of AI.
        """
    )

    st.subheader("Team 13")
    st.markdown(
        """
        Moaiad Eljack (team captain), Thomas Tarutin, Jacob Donovan, Alexander Kosak,
        Ana Huerfano Ramos, and Samuel Block.
        """
    )

    st.subheader("Acknowledgements")
    st.markdown(
        f"""
        Special thanks to our faculty mentor, **Mikhail Polyanskiy**, for his guidance throughout
        the project.

        Thank you especially to **Austin Brown** (Team 12) and **Micah Santiago** (Team 14) for their
        help in putting together the final dataset, the interface, and the presentation.

        Thank you to all of the organizers of the event.

        **GitHub repository:** [{GITHUB_REPO_URL}]({GITHUB_REPO_URL})
        """
    )


def contribute_page() -> None:
    st.header("Contribute")
    st.info(
        "The following is a sample placeholder page illustrating how a maintaining user group "
        "might operate LaserBase as an ongoing, community-curated database. The contact details "
        "and workflow below are examples, not active channels."
    )
    st.markdown(
        f"""
        A database like this is best maintained as a public scientific facility catalogue:
        facilities, user groups, and community members propose additions or corrections, and
        curators review source-backed changes before they become part of the published database.

        A user group that took ownership of LaserBase would use this page to publish their contact
        information, describe what they need from contributors, and explain how proposed changes are
        reviewed and merged.

        **GitHub repository:** [{GITHUB_REPO_URL}]({GITHUB_REPO_URL})

        **Example contact for facility additions or corrections:** `database-contact@example.org`
        """
    )

    st.subheader("What To Provide")
    st.markdown(
        """
        For a new or corrected instrument/facility entry, please provide:

        - Facility or institution name.
        - Laser/system, beamline, or representative operating mode name.
        - Country.
        - Laser type code from the key on the About page.
        - Facility status and demonstrated status.
        - Figure-of-merit values with units matching the database fields.
        - DOI, facility page, technical report, or other public source link.
        - Any note about whether the value is current, historical, demonstrated-only, planned, or representative.
        """
    )

    st.subheader("Data Entry Expectations")
    st.markdown(
        """
        - Preserve the value reported by the source whenever possible.
        - Do not enter `0` for an unavailable value.
        - Use a blank cell or `N/A` when a value is not available.
        - Do not silently convert, correct, or infer scientific values without documenting the source.
        - Prefer DOI links, facility pages, technical reports, or official user-facility documentation.
        """
    )

    st.subheader("Codespaces Workflow")
    st.markdown(
        """
        When the repository is public, contributors can open it in GitHub Codespaces, update the controlled
        source workbook, rebuild the database, preview the website, and submit a pull request for review.

        Key terminal commands are collected in `RUN_APP.md` at the top level of the repository.

        Core commands:

        ```bash
        python -m streamlit run apps/streamlit_app.py
        python -m laserdb.cli build --input combined_team13_format.xlsx --outdir data/processed --reports data/reports
        python -m laserdb.cli validate --input combined_team13_format.xlsx --reports data/reports
        python -m pytest
        ```
        """
    )


def main() -> None:
    st.set_page_config(page_title="LaserBase", layout="wide")
    apply_app_css()
    if not PROCESSED_PATH.exists():
        st.error("Processed database not found. Run `laserdb build` first.")
        st.stop()
    df = load_data(PROCESSED_PATH)
    page = sidebar_navigation()
    filtered = df
    if page == "Overview":
        overview(df)
    elif page == "Search":
        filtered = search_page(df)
    elif page == "Record Detail":
        detail_page(df)
    elif page == "Plots":
        plots_page(df)
    elif page == "Export":
        filtered = search_page(df)
        export_page(df, filtered)
    elif page == "Database Keys":
        database_keys_page()
    elif page == "About":
        about_page()
    elif page == "Contribute":
        contribute_page()


if __name__ == "__main__":
    main()
