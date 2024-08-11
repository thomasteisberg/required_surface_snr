# Required Surface SNR

## Description 

This repo contains tool and scripts developed to analyze surface signal-to-noise ratio (SNR) from CReSIS and UTIG data. The project includes the following componenets: 

**snr_finder.py:** This script is designed to process radar data from .csv and .mat files to calculate the Signal-to-Noise Ratio (SNR) for each data point from the CReSIS data. This script is particularly useful for geophysical applications where radar data needs to be analyzed to assess signal quality.

**comparer.py:** This script is designed to compare radar data from two different sources: CReSIS and UTIG. It performs spatial matching and analyzes Signal-to-Noise Ratio (SNR) values to evaluate the consistency between these datasets.

**data_scrapper.py:** This script is designed to scrape data from the CReSIS data repository website at https://data.cresis.ku.edu/data/rds/. It collects .csv and .mat files, which are subsequently saved into a user-defined directory. The script includes error handling and retry mechanisms to ensure robust file downloading.

**plot_cresis_data.py:** This script is designed to process and analyze Signal-to-Noise Ratio (SNR) data from CReSIS and UTIG datasets. It integrates data from .csv and .mat files, computes SNR values, and visualizes the results.


