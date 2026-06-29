from pathlib import Path

from laserdb.constants import REQUIRED_COLUMNS
from laserdb.io import load_laser_data, load_workbook


WORKBOOK = Path("combined_team13_format.xlsx")


def test_load_workbook_sheets():
    sheets = load_workbook(WORKBOOK)
    assert "Combined_Team13" in sheets


def test_required_columns_present():
    df = load_laser_data(WORKBOOK)
    assert list(df.columns) == REQUIRED_COLUMNS
    assert len(df) > 0
