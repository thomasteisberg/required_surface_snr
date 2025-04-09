import os
import pandas as pd
import numpy as np
from snrfinder import snrfinder
from scipy.io import loadmat
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape and download files from CReSIS data.")
    parser.add_argument('--data', type=str, default="cresis_data", help="Directory of downloaded CReSIS RDS data files")
    parser.add_argument('--dataset', type=str, default='Antarctica', help="Dataset to process (Antarctica or Greenland), case sensitive")
    parser.add_argument('--output', type=str, default='snr_data.csv', help="Output path for CSV file")
    args = parser.parse_args()

    # Top-level directories to process
    top_level_dirs = [ f.name for f in os.scandir(args.data) if f.is_dir() and args.dataset in f.name ]
    print(top_level_dirs)

    print(f"Found directories to process: {top_level_dirs}")

    snr_dfs_list = []

    stats = {tld: {'success': 0, 'no_mat': 0, 'other_failure': 0} for tld in top_level_dirs}

    for top_level_dir in top_level_dirs:
        base_dir = os.path.join(args.data, top_level_dir)
        if not os.path.isdir(base_dir):
            print(f"Directory does not exist: {base_dir}")
            continue

        # Get a list of CSV and MAT files in the folder
        csv_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(base_dir) for f in filenames if f.endswith('.csv')]
        mat_files = {os.path.splitext(f)[0]: os.path.join(dp, f) for dp, dn, filenames in os.walk(base_dir) for f in filenames if f.endswith('.mat')}

        for csvPath in csv_list:
            name = os.path.splitext(os.path.basename(csvPath))[0]

            if name not in mat_files:
                print(f'Could not find {name}.mat')
                stats[top_level_dir]['no_mat'] += 1
                continue

            matPath = mat_files[name]

            print(f'Now reading {csvPath} and {matPath}')

            try:
                snrs = snrfinder(csvPath, matPath)
                df = pd.DataFrame(snrs, columns=['x', 'y', 'snr'])
                df['source_csv_file'] = os.path.basename(csvPath)
                df['source_mat_file'] = os.path.basename(matPath)
                snr_dfs_list.append(df)
                stats[top_level_dir]['success'] += 1
            except Exception as e:
                print(f'Error processing {csvPath} and {matPath}: {e}')
                print(e)
                stats[top_level_dir]['other_failure'] += 1
                continue

    # CRESIS DATA
    df = pd.concat(snr_dfs_list, ignore_index=True)

    # Save the CSV file in a cross-platform way
    output_csv_path = args.output
    df.to_csv(output_csv_path, index=False)
    print(f'Data saved to {output_csv_path}')

    # Print a summary of the results
    print("\nSummary of results:")
    for tld, result in stats.items():
        print(f"{tld}: {result['success']} successes, {result['no_mat']} missing .mat files, {result['other_failure']} other failures")
    print(f"Total entires in exported CSV file: {len(df)}")
