import pandas as pd

from laserdb.clean import build_processed_table
from laserdb.validate import find_parse_failures, validate_database, write_validation_outputs


def test_validation_report_generation(tmp_path):
    raw = pd.DataFrame(
        {
            "laser_name": ["Alpha"],
            "year": ["2020"],
            "doi_or_link": [""],
            "laser_type": ["GS"],
            "facility": ["Lab A"],
            "country": [""],
            "facility_status": ["Operational"],
            "demonstrated_status": ["Q"],
            "peak_power_w": ["malformed"],
            "wavelength_m": ["8e-7"],
            "rep_rate_s_inv": ["1"],
            "max_intensity_w_m2": ["1e27"],
            "pulse_energy_j": ["30"],
            "pulse_duration_fs": ["30"],
        }
    )
    df = build_processed_table(raw)
    report = validate_database(df)
    assert report["unrecognized_laser_types"] == ["GS"]
    assert report["unrecognized_demonstrated_status"] == ["Q"]
    assert report["parse_failure_count"] == 1
    assert len(find_parse_failures(df)) == 1
    write_validation_outputs(df, tmp_path)
    assert (tmp_path / "validation_report.md").exists()
    assert (tmp_path / "validation_report.json").exists()
