# UK River Flow Data (GR6J and G2G)

Daily river flow data for 200 UK gauging stations, prepared for the Freshwater Digital Twin project. Derived from the eFLaG dataset (UKCEH, BGS, HR Wallingford).

**New here? Start with `Hydrology_Data_User_Guide.docx`**, it explains everything in plain language, no hydrology or programming background needed.

## Data

The four full data files (real-history and future-projection flow, for both the GR6J and G2G models, 1.7GB combined) are too large for GitHub and are hosted on Zenodo instead:

**Download the data: https://zenodo.org/records/21475449**
**DOI: https://doi.org/10.5281/zenodo.21475449**

Licensed CC-BY 4.0, free to use with attribution.

## What's in this repository

| File | What it is |
|---|---|
| `Hydrology_Data_User_Guide.docx` | Plain-language guide to the whole dataset, start here |
| `Station_Locations.xlsx` | Latitude/longitude and data-quality info for all 200 stations |
| `hydrology_download_clean.py` | Script to download and rebuild the simobs (real-history) data |
| `hydrology_simrcm_download_clean.py` | Script to download and rebuild the simrcm (future-projection) data |
| `eFLaG_Station_Metadata.xlsx` | UKCEH's original station metadata (source for Station_Locations.xlsx) |
| `eFLaG_EIDC_Supporting_Documentation.pdf` | UKCEH's official technical documentation for the full eFLaG dataset |

## Source and citation

Hannaford, J. et al. eFLaG: enhanced Future Flows and Groundwater. A national dataset of hydrological projections based on UKCP18. Earth System Science Data.

Original dataset DOI: https://doi.org/10.5285/1bb90673-ad37-4679-90b9-0126109639a9

If you use the specific cleaned/combined files from this repository, please also cite:

Emmanuel, F. (2026). GR6J and G2G River Flow Data, eFLaG-derived. Zenodo. https://doi.org/10.5281/zenodo.21475449
