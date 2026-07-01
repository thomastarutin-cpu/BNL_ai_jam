# Run The LaserBase App

LaserBase is a Streamlit web app. This file covers running it locally or in
GitHub Codespaces. The processed database is committed to the repository, so the
app works immediately after installing dependencies — no build step is required
just to browse it.

Repository: <https://github.com/thomastarutin-cpu/BNL_ai_jam>

## 1. Install Dependencies

From the repository root:

```bash
python -m pip install -e .
```

This installs the `laserdb` package (from `src/`) and every runtime dependency
declared in `pyproject.toml`. To also install the development tools (pytest,
ruff), use:

```bash
python -m pip install -e ".[dev]"
```

## 2. Start The Website

```bash
python -m streamlit run apps/streamlit_app.py
```

If the browser does not open automatically, open the URL printed by Streamlit.
In Codespaces, open the **Ports** tab and click the forwarded Streamlit port
(8501 by default).

If the default port is busy, choose one explicitly:

```bash
python -m streamlit run apps/streamlit_app.py --server.port 8601
```

Then open <http://localhost:8601>.

## 3. Rebuild The Database After Editing The Workbook

The controlled source workbook is `combined_team13_format.xlsx`. After editing
it, regenerate the processed CSV/parquet and reports:

```bash
laserdb build --input combined_team13_format.xlsx --outdir data/processed --reports data/reports
```

This writes `data/processed/laser_data_raw.csv`,
`data/processed/laser_data_processed.csv`,
`data/processed/laser_data_normalized.parquet`, and the reports in
`data/reports/`. The app reads `data/processed/laser_data_processed.csv`.

(`laserdb` is installed as a console script by step 1. The equivalent
`python -m laserdb.cli build ...` also works.)

## 4. Validate And Test Before Sharing Changes

```bash
laserdb validate --input combined_team13_format.xlsx --reports data/reports
python -m pytest
```

Validation flags suspicious or incomplete records for review; it never silently
corrects scientific values.
