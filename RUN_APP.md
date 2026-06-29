# Run The LaserBase App

Use this file when opening the repository in GitHub Codespaces or a local terminal.

## Start The Website

From the repository root, run:

```bash
o
```

If the browser does not open automatically, open the URL printed by Streamlit. In Codespaces, use the **Ports** tab and open the forwarded Streamlit port.

If the default port is busy, choose a port explicitly:

```bash
python -m streamlit run apps/streamlit_app.py --server.address 0.0.0.0 --server.port 8601
```

Then open:

```text
http://localhost:8601
```

## Rebuild The Database After Editing The Workbook

The controlled source workbook lives at:

```text
combined_team13_format.xlsx
```

After updating it, run:

```bash
python -m laserdb.cli build --input combined_team13_format.xlsx --outdir data/processed --reports data/reports
```

## Validate Before Sharing Changes

```bash
python -m laserdb.cli validate --input combined_team13_format.xlsx --reports data/reports
python -m pytest
```

## Public Repository Placeholder

The public repository link will be added here when the project is published:

```text
https://github.com/your-org/laser-facility-database
```
