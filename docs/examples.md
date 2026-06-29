# Examples

## Search For Petawatt-Class Facilities

```python
import pandas as pd
from laserdb.search import search_lasers

df = pd.read_csv("data/processed/laser_data_processed.csv")
result = search_lasers(df, filters={"petawatt_class": True}, sort_by="peak_power_desc")
```

## Find FEL Entries By Country

```python
fel = search_lasers(df, filters={"laser_type": ["FEL"]}, sort_by="country")
```

## Wavelength Near 800 nm

```python
near_800 = search_lasers(df, filters={"wavelength_nm": (750, 850)})
```

## Create A Plot

```python
from laserdb.plotting import peak_power_vs_duration

fig = peak_power_vs_duration(df)
fig.show()
```
