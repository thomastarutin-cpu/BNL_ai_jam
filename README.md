# LaserBase

This repository turns `combined_team13_format.xlsx` into a reusable Python package, validation workflow, searchable catalogue, plotting toolkit, and Streamlit app for high-power lasers, FELs, and related user facilities.

The current database is a structured survey table, not a final authoritative registry. Figure-of-merit values come from heterogeneous sources. Some records represent facilities, some specific beamlines, and some representative operating modes. Missing values are unknown values, not zeros.

## What Is Included

- Raw workbook preservation in `data/raw/`.
- Source-derived raw CSV in `data/processed/laser_data_raw.csv`.
- Processed CSV and parquet exports with derived columns.
- Validation reports for missingness, parse failures, unrecognized codes, and gentle outlier review.
- A reusable package in `src/laserdb`.
- A `laserdb` CLI.
- A professional Streamlit catalogue in `apps/streamlit_app.py`.
- Plotly figure helpers and generated HTML figures.
- Tests and example notebooks.

Raw FOM columns are never overwritten. Numeric and display-unit columns are generated separately for search and plotting.

## Installation

```bash
python -m pip install -e ".[dev]"
```

In Codespaces, run the same command from the repository root.

## Rebuild The Database

```bash
laserdb build --input combined_team13_format.xlsx --outdir data/processed
```

This writes:

- `data/processed/laser_data_raw.csv`
- `data/processed/laser_data_processed.csv`
- `data/processed/laser_data_normalized.parquet`
- validation and summary reports in `data/reports/`

## Validate

```bash
laserdb validate --input combined_team13_format.xlsx --reports data/reports
```

Validation flags suspicious or incomplete records for review. It does not silently correct scientific values.

## Launch The App

```bash
python -m streamlit run apps/streamlit_app.py
```

The app includes overview metrics, searchable tables, Record Detail cards, Plotly figures, and downloads.

## Example Searches

```bash
laserdb search --query ELI --laser-type HY --min-power-pw 1
laserdb search --country USA --min-power-pw 1
laserdb summary --group-by country
laserdb figures --outdir figures
```

Python API:

```python
import pandas as pd
from laserdb.search import search_lasers

df = pd.read_csv("data/processed/laser_data_processed.csv")
petawatt_800nm = search_lasers(
    df,
    filters={"petawatt_class": True, "wavelength_nm": (700, 900)},
    sort_by="peak_power_desc",
)
```

## Current Limitations

- The source table is incomplete by design.
- Facility status strings are preserved and only coarsely grouped for filtering.
- Laser type acronyms are not recategorized. Noncanonical codes are reported by validation.
- Derived numeric columns are parsing conveniences, not new scientific claims.
- Source verification and literature follow-up remain future curation tasks.

## Contribution Workflow

Contributors should preserve raw source values, include a DOI or facility/source link when available, and run validation before opening a pull request. Suspicious values should be discussed in review rather than silently corrected.

See `docs/contribution_guide.md` for the full workflow and PR checklist.
