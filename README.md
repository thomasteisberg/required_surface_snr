## Dataset creation workflow

### Step 1: Download the relevant CReSIS RDS data

#### On Sherlock:

```
cd data_preprocessing/slurm
sbatch get_cresis_antarctica.sh
sbatch get_cresis_greenland.sh
```

#### General instructions

See [data_preprocessing README](data_preprocessing/README.md).

### Step 2: Extract surface SNR from RDS data

#### On Sherlock:

```
cd data_preprocessing/slurm
sbatch run_raw_to_snr.sh
```

#### General instructions:

Run `raw_to_snr.py` for each dataset.

```
cd data_preprocessing
python raw_to_snr.py --dataset Greenland --output snr_data_cresis_gis.csv
python raw_to_snr.py --dataset Antarctica --output snr_data_cresis_ais.csv
```

##### Summaries and notes

Below are the summaries printed for each of the two ice sheets. Some years do not have much or any data included in the dataset due to various data availability issues.

Antarctic Ice Sheet:

```
Summary of results:
2017_Antarctica_Basler: 0 successes, 469 missing .mat files, 0 other failures
2010_Antarctica_DC8: 38 successes, 408 missing .mat files, 0 other failures
2009_Antarctica_TO: 0 successes, 579 missing .mat files, 0 other failures
2012_Antarctica_DC8: 638 successes, 24 missing .mat files, 0 other failures
2011_Antarctica_TO: 462 successes, 58 missing .mat files, 5 other failures
2019_Antarctica_GV: 412 successes, 29 missing .mat files, 0 other failures
2018_Antarctica_DC8: 809 successes, 27 missing .mat files, 0 other failures
2017_Antarctica_P3: 188 successes, 12 missing .mat files, 0 other failures
2016_Antarctica_DC8: 1126 successes, 57 missing .mat files, 0 other failures
2011_Antarctica_DC8: 0 successes, 1047 missing .mat files, 0 other failures
2013_Antarctica_Basler: 0 successes, 439 missing .mat files, 0 other failures
2014_Antarctica_DC8: 1061 successes, 78 missing .mat files, 0 other failures
2013_Antarctica_P3: 285 successes, 7 missing .mat files, 0 other failures
2023_Antarctica_BaslerMKB: 575 successes, 25 missing .mat files, 0 other failures
2022_Antarctica_BaslerMKB: 502 successes, 25 missing .mat files, 0 other failures
2009_Antarctica_TO_Gambit: 224 successes, 719 missing .mat files, 0 other failures
2009_Antarctica_DC8: 71 successes, 792 missing .mat files, 0 other failures
Total entires in exported CSV file: 14995946
```

Greenland Ice Sheet:

```
Summary of results:
2011_Greenland_P3: 0 successes, 1801 missing .mat files, 0 other failures
2018_Greenland_P3: 843 successes, 23 missing .mat files, 0 other failures
2015_Greenland_C130: 1558 successes, 84 missing .mat files, 0 other failures
2011_Greenland_TO: 0 successes, 316 missing .mat files, 0 other failures
2014_Greenland_P3: 1864 successes, 60 missing .mat files, 0 other failures
2016_Greenland_P3: 551 successes, 43 missing .mat files, 0 other failures
2016_Greenland_TOdtu: 90 successes, 20 missing .mat files, 0 other failures
2010_Greenland_DC8: 238 successes, 419 missing .mat files, 0 other failures
2013_Greenland_P3: 878 successes, 31 missing .mat files, 0 other failures
2016_Greenland_Polar6: 0 successes, 71 missing .mat files, 0 other failures
2017_Greenland_P3: 1703 successes, 48 missing .mat files, 0 other failures
2016_Greenland_G1XB: 29 successes, 8 missing .mat files, 0 other failures
2010_Greenland_P3: 0 successes, 649 missing .mat files, 0 other failures
2019_Greenland_P3: 1236 successes, 38 missing .mat files, 0 other failures
2012_Greenland_P3: 1891 successes, 234 missing .mat files, 0 other failures
Total entires in exported CSV file: 24050835
```

In the cases I've looked into, the "missing .mat files" are due to the correct level of processing not being available. This script expects the `CSARP_qlook` level of processing with all chirps merged (if a waveform playlist is used, which it generally is on these).

**TODO: We are currently using the `CSARP_qlook` level of processing, which generally has somewhat worse availability compared to `CSARP_qlook`. The rationale behind starting with qlook (unfocused SAR) is that it is most similar to the processing we think was done on the UTIG dataset, however we should (1) re-confirm what processing was actually done on the UTIG data we have and (2) explore if we can correct for changes due to focusing.**

### Step 3: Acquire external datasets

Several external datasets are used as input data. Each of these datasets will be interpolated in step 4 to apply labels to each of the radar surface SNR points.

The table below shows a summary of the data sources:

| Data Type | Greenland IS Source | Antarctic IS Source |
| --- | --- | --- |
| Ice Thickness and Floating Mask | [BedMachine Greenland (NSIDC IDBMG4)](https://nsidc.org/data/idbmg4/versions/5) | [BedMachine Antarctica (NSIDC-0756)](https://nsidc.org/data/nsidc-0756/versions/3) |
| Surface Velocity | [NASA ITS_LIVE 120 m Mosaic](https://its-live.jpl.nasa.gov/) [(Direct S3 data link)](https://its-live-data.s3.amazonaws.com/velocity_mosaic/v2/static/ITS_LIVE_velocity_120m_RGI05A_0000_v02.nc) | [MEaSUREs Phase-Based Antarctic Surface Velocities (NSIDC-0754)](https://nsidc.org/data/nsidc-0754/versions/1) |
| 2 m Surface Temperature | [ECMWF ERA5 Monthly Averages](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=overview) |

Note that the ERA5 2 meter surface temperature dataset is global, so the same data file is used for both ice sheets.

Except for the ERA5 dataset, all of these datasets can be automatically downloaded by running the `external_datasets/download_datasets.sh` script. The script will prompt you for your NASA Earthdata username and password. If you don't have an account, you can [make one for free](https://urs.earthdata.nasa.gov/users/new).

The ERA5 dataset can be accessed [here](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=overview). Details of the requsted dataset are as follows:

```
dataset = "reanalysis-era5-single-levels-monthly-means"
request = {
    "product_type": ["monthly_averaged_ensemble_members"],
    "variable": ["2m_temperature"],
    "year": [
        "2018", "2019", "2020",
        "2021", "2022", "2023"
    ],
    "month": ["01"],
    "time": ["00:00"],
    "data_format": "netcdf",
    "download_format": "unarchived"
}
```

### Step 4: Interpolate external datasets to radar data

Finally, the notebook `interpolate_external_datasets.ipynb` is used to do a nearest neighbors interpolation of each of the input datasets to the radar data. It also sub-samples the radar data to produce a reasonable along-track spacing.

The notebook must be run once for each of the separate datasets (CReSIS/Antarctica, CReSIS/Greenland, UTIG/Antarctica). Uncomment the appropriate line in the "Dataset options" cell.
