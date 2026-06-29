# Schema

The canonical source table is the `laser_data` worksheet. It must contain these columns:

```text
laser_name, year, doi_or_link, laser_type, facility, country,
facility_status, demonstrated_status, peak_power_w, wavelength_m,
rep_rate_s_inv, max_intensity_w_m2, pulse_energy_j, pulse_duration_fs
```

The processed table retains every source column and appends derived fields. Validation flags incomplete records but does not drop them.

Primary validation rules:

- Required columns must exist.
- `record_id` values should be unique.
- `laser_type` and `demonstrated_status` values should be recognized or explicitly reviewed.
- Numeric parse failures are reported per cell.
- Missing source, country, facility, and name fields are reported.
- FOM missingness is summarized by record and by column.
- Potential unit outliers are flagged for review only.
