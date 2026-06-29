import math

import pandas as pd

from laserdb.clean import add_display_unit_columns, add_numeric_fom_columns, parse_numeric_value


def test_parse_numeric_common_cases():
    assert parse_numeric_value("1e+27") == 1e27
    assert parse_numeric_value("0.00000105") == 0.00000105
    assert math.isnan(parse_numeric_value("N/A"))
    assert math.isnan(parse_numeric_value("NA"))
    assert math.isnan(parse_numeric_value(""))
    assert parse_numeric_value("\u00a01e15\u00a0") == 1e15
    assert math.isnan(parse_numeric_value("about 1e15"))
    assert parse_numeric_value("8.2e_7", "wavelength_m") == 8.2e-7
    assert math.isnan(parse_numeric_value("8.2e_7", "peak_power_w"))


def test_display_unit_conversion():
    df = pd.DataFrame(
        {
            "peak_power_w": ["1e15"],
            "wavelength_m": ["8e-7"],
            "rep_rate_s_inv": ["10"],
            "max_intensity_w_m2": ["1e27"],
            "pulse_energy_j": ["30"],
            "pulse_duration_fs": ["30"],
            "year": ["2024"],
        }
    )
    out = add_display_unit_columns(add_numeric_fom_columns(df))
    assert out.loc[0, "peak_power_pw"] == 1
    assert out.loc[0, "wavelength_nm"] == 800
    assert out.loc[0, "pulse_duration_ps"] == 0.03
