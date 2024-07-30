import requests
from bs4 import BeautifulSoup
import os
import time

# Base URL for the main directory
base_url = "https://data.cresis.ku.edu/data/rds/"

# Directory to save the downloaded files
download_dir = "cresis_data"
os.makedirs(download_dir, exist_ok=True)

# Log file to keep track of progress
log_file = "download_log.txt"

# Function to read the log file
def read_log():
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            return set(line.strip() for line in file)
    return set()

# Function to write to the log file
def write_log(entry):
    with open(log_file, 'a') as file:
        file.write(f"{entry}\n")

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
                write_log(url)
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
def scrape_files(base_url, subdir, file_ext, subfolder='', exclude_keyword=None):
    url = f"{base_url}{subdir}{subfolder}".rstrip('/') + '/'
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

    downloaded_files = read_log()

    if files:
        subdir_path = os.path.join(download_dir, subdir.replace('/', '_'), subfolder.replace('/', '_'))
        os.makedirs(subdir_path, exist_ok=True)
        for file in files:
            file_url = url + file
            download_path = os.path.join(subdir_path, file)
            if file_url not in downloaded_files:
                download_file(file_url, download_path)

    for directory in directories:
        print(f"Found subdirectory: {directory}, navigating into it")
        new_subfolder = os.path.join(subfolder.rstrip('/'), directory.lstrip('/'))
        scrape_files(base_url, subdir, file_ext, new_subfolder, exclude_keyword)

# Function to get the list of relevant directories
def get_relevant_directories(base_url):
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
        if href and 'Antarctica' in href:
            year = href.split('_')[0]
            if year.isdigit() and 2018 <= int(year) <= 2022:
                relevant_dirs.append(href)
    if not relevant_dirs:
        print("No relevant directories found")
    return relevant_dirs

# Main code to scrape data for the years 2018 to 2023
relevant_directories = get_relevant_directories(base_url)
for subdir in relevant_directories:
    print(f"Scraping data from {subdir}")
    scrape_files(base_url, subdir, '.csv', subfolder='csv/', exclude_keyword='GroundGHOST')
    scrape_files(base_url, subdir, '.mat', subfolder='CSARP_qlook/', exclude_keyword='_img_')
