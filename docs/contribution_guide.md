# Contribution Guide

## Adding A Facility Or Laser Row

Add or edit records in the controlled input workbook or a reviewed CSV template. Preserve source values exactly as reported. Do not convert units in the raw FOM columns unless the source table itself is being deliberately curated and reviewed.

Every record should include:

- Laser/system name.
- Facility or institution.
- Country.
- Laser type code.
- Facility status.
- Demonstrated status.
- DOI or facility/source link when available.

## Citing Sources

Prefer DOI links for publications. Facility pages, technical reports, conference proceedings, or official user-facility descriptions are acceptable when no DOI exists. Leave the source blank only when no provenance is currently known; validation will flag the record.

## Uncertain Values

Do not guess missing scientific values. Leave the raw cell blank or use an accepted missing token. Add discussion in the pull request describing what source verification is needed.

## Corrections

Corrections should include the source supporting the change. If a value appears suspicious but the source is unclear, open an issue or PR note rather than silently replacing it.

## Validation

Run:

```bash
laserdb build
laserdb validate
pytest
```

Validation checks required columns, duplicate IDs, code dictionaries, parse failures, source coverage, missingness, incomplete FOMs, and gentle unit outlier ranges.

## Pull Request Checklist

- Raw source values are preserved.
- New or changed records include DOI/source links where possible.
- Missing values are not encoded as zero.
- Validation report has been reviewed.
- Unrecognized codes are intentional or corrected with a documented project alias.
- Tests pass.
