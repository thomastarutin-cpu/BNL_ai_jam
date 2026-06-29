"""Project constants for the laser facility database."""

REQUIRED_COLUMNS = [
    "laser_name",
    "year",
    "doi_or_link",
    "laser_type",
    "facility",
    "country",
    "facility_status",
    "demonstrated_status",
    "peak_power_w",
    "wavelength_m",
    "rep_rate_s_inv",
    "max_intensity_w_m2",
    "pulse_energy_j",
    "pulse_duration_fs",
]

CORE_COMPLETENESS_COLUMNS = [
    "laser_name",
    "year",
    "doi_or_link",
    "laser_type",
    "facility",
    "country",
    "facility_status",
    "demonstrated_status",
]

FOM_COLUMNS = [
    "peak_power_w",
    "wavelength_m",
    "rep_rate_s_inv",
    "max_intensity_w_m2",
    "pulse_energy_j",
    "pulse_duration_fs",
]

FOM_NUMERIC_COLUMNS = {
    "peak_power_w": "peak_power_w_num",
    "wavelength_m": "wavelength_m_num",
    "rep_rate_s_inv": "rep_rate_hz_num",
    "max_intensity_w_m2": "max_intensity_w_m2_num",
    "pulse_energy_j": "pulse_energy_j_num",
    "pulse_duration_fs": "pulse_duration_fs_num",
}

DISPLAY_UNIT_COLUMNS = {
    "peak_power_pw": ("peak_power_w_num", 1e-15),
    "wavelength_nm": ("wavelength_m_num", 1e9),
    "wavelength_um": ("wavelength_m_num", 1e6),
    "rep_rate_hz": ("rep_rate_hz_num", 1.0),
    "max_intensity_w_cm2": ("max_intensity_w_m2_num", 1e-4),
    "pulse_duration_ps": ("pulse_duration_fs_num", 1e-3),
}

LASER_TYPE_CODES = {
    "SS": "Solid-state bulk laser",
    "OP": "Optical parametric laser",
    "HY": "Hybrid solid-state / parametric laser",
    "GAS": "Gas laser",
    "FIB": "Fiber laser",
    "DIO": "Semiconductor / diode laser",
    "FEL": "Free-electron laser",
    "DYE": "Dye laser",
    "CHEM": "Chemical laser",
    "UNK": "Unknown / not yet classified",
}

LASER_TYPE_ALIASES: dict[str, str] = {}

DEMONSTRATED_STATUS = {
    "Y": "Demonstrated",
    "N": "Not demonstrated / planned / not demonstrated at stated performance",
    "O": "Other / partial / representative / operational context requiring interpretation",
}

MISSING_VALUE_TOKENS = {"", "na", "n/a", "nan", "none", "null", "-", "unknown", "not reported"}

COUNTRY_NORMALIZATION = {
    "US": "USA",
    "U.S.": "USA",
    "United States": "USA",
    "United States of America": "USA",
}

SORT_COLUMNS = {
    "peak_power_desc": ("peak_power_w_num", False),
    "rep_rate_desc": ("rep_rate_hz_num", False),
    "pulse_energy_desc": ("pulse_energy_j_num", False),
    "pulse_duration_asc": ("pulse_duration_fs_num", True),
    "year_desc": ("year_num", False),
    "country": ("country", True),
    "facility": ("facility", True),
    "name": ("laser_name", True),
}
