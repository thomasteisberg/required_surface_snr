# Required Surface SNR

## Overview

This repository contains a comprehensive suite of tools and scripts designed for analyzing the surface Signal-to-Noise Ratio (SNR) from CReSIS and UTIG radar datasets. These tools facilitate the processing, comparison, and visualization of radar data, offering valuable insights into signal quality and consistency across different datasets.

## Components

### **1. `snr_finder.py`**

**Description:**  
This script processes radar data from `.csv` and `.mat` files to calculate the Signal-to-Noise Ratio (SNR) for each data point in the CReSIS dataset. It is robust and efficient, ideal for large geophysical radar datasets. The calculated SNR values are crucial for determining the quality and reliability of radar signals in various environments.

### **2. `comparer.py`**

**Description:**  
This script compares radar data from two different sources: CReSIS and UTIG. It performs spatial matching of the datasets and analyzes the SNR values to evaluate the consistency and reliability of radar data across different sources.

### **3. `data_scrapper.py`**

**Description:**  
This script automates the process of scraping radar data from the [CReSIS data repository](https://data.cresis.ku.edu/data/rds/). It downloads `.csv` and `.mat` files and saves them into a user-defined directory, ensuring reliable and uninterrupted data collection with built-in error handling and retry mechanisms.

### **4. `plot_cresis_data.py`**

**Description:**  
This script processes and visualizes SNR data from CReSIS and UTIG datasets. It integrates data from `.csv` and `.mat` files, computes SNR values, and generates visual representations of the results. This tool is invaluable for data analysis and presentation, providing insights into the quality and distribution of radar signals.

## Installation

To use the tools in this repository, clone the repo and install the required dependencies:

```bash
git clone https://github.com/yourusername/required_surface_snr.git
cd required_surface_snr
pip install -r requirements.txt


