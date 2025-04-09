'''
This script is designed to scrap data from https://data.cresis.ku.edu/data/rds/
website to collect .csv and .mat files to be latter used. This script includes
error handling and saves the files to a directory the user names (it is named here
"cresis_data").

Code by: Adam Alhousiki

'''

import requests
from bs4 import BeautifulSoup
import os
import time
import argparse

# Function to download files with retry logic
def download_file(url, download_path, retries=3, backoff_factor=1):
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(download_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive new chunks
                            file.write(chunk)
                print(f"Downloaded: {url}")
                return True
            else:
                print(f"Failed to download: {url} with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            if attempt < retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to download {url} after {retries} attempts")
                return False
    return False

# Function to scrape files from a specific directory
def scrape_files(url, download_dir, file_ext, exclude_keyword=None):
    print(f"Accessing URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to access {url}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')

    files = []
    directories = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith(file_ext) and (exclude_keyword is None or exclude_keyword not in href):
            files.append(href)
        elif href and href.endswith('/') and not href.startswith('../') and not href.startswith('/'):
            directories.append(href)

    if files:
        os.makedirs(download_dir, exist_ok=True)
        for file in files:
            file_url = os.path.join(url, file)
            download_path = os.path.join(download_dir, file)
            download_file(file_url, download_path)

    for directory in directories:
        print(f"Found subdirectory: {directory}, navigating into it")
        new_url = os.path.join(url, directory)
        new_download_dir = os.path.join(download_dir, directory)
        scrape_files(new_url, new_download_dir, file_ext, exclude_keyword=exclude_keyword)

# Function to get the list of relevant directories
def get_relevant_directories(base_url, dataset='Antarctica', year=2023, exclude_keywords=None):
    print(f"Accessing base URL: {base_url}")
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to access {base_url}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')

    relevant_dirs = []
    for link in soup.find_all('a'):
        href = link.get('href')
        print(f"Found href: {href}")
        if href and dataset in href: # Match dataset: Antarctica or Greenland
            if exclude_keywords:
                if any(keyword in href for keyword in exclude_keywords):
                    continue
            year_str = href.split('_')[0]
            if int(year_str) == year: # Match year
                relevant_dirs.append(href)
    if not relevant_dirs:
        print("No relevant directories found")
    return relevant_dirs

# Base URL for the main directory
base_url = "https://data.cresis.ku.edu/data/rds/"

# Filters for data to download
year = 2023
dataset = 'Antarctica'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and download files from CReSIS data.")
    parser.add_argument('--download_dir', type=str, default="cresis_data", help="Directory to save downloaded files")
    parser.add_argument('--year', type=int, default=2023, help="Year to scrape data for")
    parser.add_argument('--dataset', type=str, default='Antarctica', help="Dataset to scrape data for (Antarctica or Greenland), case sensitive")
    args = parser.parse_args()

    download_dir = args.download_dir
    year = args.year
    dataset = args.dataset
    os.makedirs(download_dir, exist_ok=True)

    print("Looking for relevant directories for dataset:", dataset, "and year:", year)

    relevant_directories = get_relevant_directories(base_url, dataset=dataset, year=year, exclude_keywords=['Ground', 'ground'])
    for subdir in relevant_directories:
        print(f"Scraping data from {subdir}")
        scrape_files(os.path.join(base_url, subdir, 'csv'), os.path.join(download_dir, subdir, 'csv'), '.csv')
        scrape_files(os.path.join(base_url, subdir, 'CSARP_qlook'), os.path.join(download_dir, subdir, 'CSARP_qlook'), '.mat', exclude_keyword='_img_')
