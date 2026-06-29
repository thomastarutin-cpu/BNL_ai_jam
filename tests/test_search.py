import pandas as pd

from laserdb.clean import build_processed_table
from laserdb.search import search_lasers


def sample_df():
    raw = pd.DataFrame(
        {
            "laser_name": ["Alpha", "Beta"],
            "year": ["2020", "2021"],
            "doi_or_link": ["https://example.com", ""],
            "laser_type": ["SS", "FEL"],
            "facility": ["Lab A", "Light Source B"],
            "country": ["USA", "Germany"],
            "facility_status": ["Operational", "Demonstrated"],
            "demonstrated_status": ["Y", "O"],
            "peak_power_w": ["2e15", "1e12"],
            "wavelength_m": ["8e-7", "1e-9"],
            "rep_rate_s_inv": ["1", "1000"],
            "max_intensity_w_m2": ["1e27", ""],
            "pulse_energy_j": ["30", ""],
            "pulse_duration_fs": ["30", "100"],
        }
    )
    return build_processed_table(raw)


def test_search_text_and_power_filter():
    result = search_lasers(sample_df(), query="Lab A", filters={"petawatt_class": True})
    assert result["laser_name"].tolist() == ["Alpha"]


def test_filter_laser_type():
    result = search_lasers(sample_df(), filters={"laser_type": ["FEL"]})
    assert result["country"].tolist() == ["Germany"]
