# ChemFate dummy input data — README

These are **plausible** values for a hypothetical run of ChemFate on the **River Tame catchment** for the year **2024**, with three test chemicals: **diclofenac, zinc, and benzo[a]pyrene**.

The values are illustrative only. They were generated with realistic ranges for the UK and reasonable seasonal patterns, but they were not measured or downloaded from any actual data source. Use these files only to test your pipeline (loading, joining, formatting, error handling). Do not draw any scientific conclusions from them.

---

## Files

### 01_climate_flow_daily_Tame_2024.csv (366 rows)
Daily climate-and-flow time series for one whole year.

- `date` — ISO date string, YYYY-MM-DD.
- `T_air_C` — daily mean air temperature in degrees Celsius. Realistic UK seasonal cycle: ~3 °C in winter, ~17 °C in summer.
- `precipitation_mm` — daily total precipitation in millimetres. Skewed distribution: many dry days, occasional wet days reaching ~25 mm.
- `wind_speed_ms` — daily mean 10 m wind speed in metres per second. Around 4–5 m/s on average, slightly higher in winter.
- `river_flow_m3s` — daily mean river flow at the catchment outlet in cubic metres per second. Baseline ~3 m³/s, peaks after wet days.

### 02_landscape_static_Tame.csv (1 row)
Static landscape descriptors for the catchment. One value per variable, applied throughout the run.

- `region_name` — your label for the region.
- `oc_fraction_percent` — soil organic carbon fraction, percent. ~4% is typical for UK mineral soils.
- `bulk_density_kg_m3` — soil bulk density, kg per cubic metre. ~1350 is typical for UK mineral soils.
- `urban_percent`, `agricultural_percent`, `natural_percent` — land use breakdown, must sum to 100. Tame is heavily urban (38%) because Birmingham sits at its head.

### 03_chemical_properties.csv (3 rows)
One row per chemical. ChemFate runs one chemical at a time, but you keep them in one table for convenience.

- `chemical_name`, `CAS_number`, `SMILES` — chemical identifiers.
- `log_Kow` — octanol-water partition coefficient, dimensionless. Not applicable to metals (NaN).
- `Koc` — organic-carbon partition coefficient, L/kg. For metals use Kd instead (NaN here, see notes).
- `Henrys_constant_Pa_m3_mol` — Henry's law constant. Zero for metals (do not volatilise).
- `half_life_air_d`, `half_life_water_d`, `half_life_soil_d`, `half_life_sediment_d` — degradation half-lives in days. NaN for metals (no degradation).
- `pKa_if_ionisable` — ionisation constant. Only required for ionisable organics (diclofenac in this set).
- `source_*` columns — where each value came from. Critical for reproducibility.
- `notes` — free-text caveats.

### 04a / 04b / 04c emissions files (366 rows each)
One file per chemical. Daily releases to each of three media (air, water, soil), in kilograms per day.

- `date` — ISO date string.
- `emission_air_kg_d` — release rate to air, kg/day.
- `emission_water_kg_d` — release rate to water, kg/day.
- `emission_soil_kg_d` — release rate to soil, kg/day.

The patterns reflect real-world expectations for these chemicals in a UK urban catchment:

- **Diclofenac:** continuous release to water via wastewater treatment works, with a slight summer peak (more medicine usage). Zero air/soil emissions.
- **Zinc:** mostly to water from urban runoff (peaks on wet days), with smaller air/soil emissions from combustion and tyre wear.
- **Benzo[a]pyrene:** mostly to air from combustion (slight winter peak from heating), tiny direct release to water. Zero soil.

---

## How these become ChemFate inputs

ChemFate has a configuration file that points to each of these CSVs. You will:

1. Load the climate-and-flow CSV → ChemFate reads it and uses each daily row as the meteorological and hydrological forcing for that day.
2. Load the landscape CSV → ChemFate uses the single row as the static parameters of the modelled region (compartment volumes, soil properties, land-use fractions).
3. Load the chemical properties CSV → ChemFate selects one chemical and pulls its log Kow, Koc, Henry, half-lives, and (if applicable) pKa to compute the fugacity capacities and transfer coefficients.
4. Load the matching emissions CSV → ChemFate uses each daily row as the source term E_i in the mass balance equation.

The exact format ChemFate expects (column names, units, headers) is in the documentation that ships with the GitHub release. Compare your file structure to the worked example in the ChemFate repository before your first run.

---

## Year length note

The 2024 file has 366 rows because 2024 was a leap year. A non-leap year (e.g. 2025) would have 365.
