# Data Dictionary

## Source Columns

| Column | Definition | Unit / Convention |
|---|---|---|
| `laser_name` | Human-readable laser, beamline, or representative operating mode. | Text |
| `year` | Publication, report, demonstration, or representative year. | Year |
| `doi_or_link` | DOI or URL provenance. | Text |
| `laser_type` | Project acronym such as `SS`, `OP`, `HY`, `GAS`, `FIB`, `DIO`, `FEL`. | Code |
| `facility` | Standardized facility or institution name. | Text |
| `country` | Standardized country name. Current convention uses `USA`. | Text |
| `facility_status` | Human-readable status string. | Text |
| `demonstrated_status` | Compact demonstrated flag. | `Y`, `N`, `O` |
| `peak_power_w` | Peak power source value. | W |
| `wavelength_m` | Wavelength source value. | m |
| `rep_rate_s_inv` | Repetition rate source value. | s^-1 / Hz |
| `max_intensity_w_m2` | Maximum intensity source value. | W/m^2 |
| `pulse_energy_j` | Pulse energy source value. | J |
| `pulse_duration_fs` | Pulse duration source value. | fs |

Missing tokens include blank strings, whitespace-only strings, `N/A`, `NA`, `n/a`, `nan`, `none`, and `null`.

## Laser Type Key

- `SS`: Solid-state bulk laser
- `OP`: Optical parametric laser
- `HY`: Hybrid solid-state / parametric laser
- `GAS`: Gas laser
- `FIB`: Fiber laser
- `DIO`: Semiconductor / diode laser
- `FEL`: Free-electron laser
- `DYE`: Dye laser
- `CHEM`: Chemical laser
- `UNK`: Unknown / not yet classified

Unknown or older codes are reported by validation rather than rewritten.

## Demonstrated Status Key

- `Y`: Demonstrated
- `N`: Not demonstrated / planned / not demonstrated at stated performance
- `O`: Other / partial / representative / operational context requiring interpretation

## Derived Columns

- `record_id`: Stable slug from laser name, facility, year, and a short hash.
- `*_num`: Parsed numeric FOM values.
- `peak_power_pw`: `peak_power_w_num / 1e15`.
- `wavelength_nm`: `wavelength_m_num * 1e9`.
- `wavelength_um`: `wavelength_m_num * 1e6`.
- `rep_rate_hz`: Alias of `rep_rate_hz_num`.
- `max_intensity_w_cm2`: `max_intensity_w_m2_num / 1e4`.
- `pulse_duration_ps`: `pulse_duration_fs_num / 1000`.
- `source_kind`: `doi`, `url`, `missing`, or `other`.
- `has_source`: Boolean source availability flag.
- `is_petawatt_class`: `peak_power_w_num >= 1e15`.
- `is_multipetawatt_class`: `peak_power_w_num >= 2e15`.
- `is_10pw_class`: `peak_power_w_num >= 1e16`.
- `wavelength_band`: Coarse plotting/search category.
- `facility_status_group`: Coarse status category.
- `demonstrated_label`: Human-readable demonstrated-status label.
- `completeness_score`: Fraction of core metadata fields present.
- `fom_completeness_score`: Fraction of FOM numeric values parsed.
