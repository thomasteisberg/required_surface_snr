import os
from tkinter import filedialog
from tkinter import Tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from snrfinder import snrfinder

# Hide the root window of Tkinter
root = Tk()
root.withdraw()

# Specify the folder where the files live
myFolder = filedialog.askdirectory(title="Select the cresis_data folder")

# Check to make sure that folder actually exists. Warn user if it doesn't.
if not os.path.isdir(myFolder):
    print(f'Error: The following folder does not exist:\n{myFolder}\nPlease specify a new folder.')
    myFolder = filedialog.askdirectory(title="Select the cresis_data folder")
    if myFolder == '':
        # User clicked Cancel
        exit()

# Top-level directories to process
top_level_dirs = ['2023_Antarctica_BaslerMKB_', '2022_Antarctica_BaslerMKB_', '2018_Antarctica_DC8_', '2019_Antarctica_GV_']

# Process each top-level directory
all_snr_data = []

for top_level_dir in top_level_dirs:
    base_dir = os.path.join(myFolder, top_level_dir)
    if not os.path.isdir(base_dir):
        print(f"Directory does not exist: {base_dir}")
        continue

    # Get a list of all csv and mat subdirectories in the respective directories
    csv_subdirs = [d for d in os.listdir(base_dir) if d.startswith('csv_') and os.path.isdir(os.path.join(base_dir, d))]
    mat_subdirs = [d for d in os.listdir(base_dir) if d.startswith('CSARP_qlook_') and os.path.isdir(os.path.join(base_dir, d))]

    for csv_subdir in csv_subdirs:
        csv_subdir_path = os.path.join(base_dir, csv_subdir)
        corresponding_mat_subdir = csv_subdir.replace('csv_', 'CSARP_qlook_')
        mat_subdir_path = os.path.join(base_dir, corresponding_mat_subdir)

        if not os.path.exists(mat_subdir_path):
            print(f"Matching directory not found for {csv_subdir_path}")
            continue

        csv_files = [os.path.join(csv_subdir_path, f) for f in os.listdir(csv_subdir_path) if f.endswith('.csv')]
        mat_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(mat_subdir_path) for f in filenames if f.endswith('.mat')]

        for csv_file in csv_files:
            csv_name = os.path.splitext(os.path.basename(csv_file))[0]

            matched_mat_files = [mat_file for mat_file in mat_files if csv_name in os.path.splitext(os.path.basename(mat_file))[0]]

            if not matched_mat_files:
                print(f'Could not find a matching .mat file for {csv_file}')
                continue

            for matched_mat_file in matched_mat_files:
                print(f'Now reading {csv_file} and {matched_mat_file}')
                snrs = snrfinder(csv_file, matched_mat_file)
                all_snr_data.append(snrs)

if all_snr_data:
    all_snr_data = np.vstack(all_snr_data)

    x = all_snr_data[:, 0]
    y = all_snr_data[:, 1]
    snr = all_snr_data[:, 2]

    plt.scatter(x, y, c=snr, s=20, cmap='viridis', edgecolor='k', alpha=0.75)
    cb = plt.colorbar()
    cb.set_label('snr')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title('SNR over Polar Stereographic Coordinates')
    plt.show()

    # Check if any coordinates are close/line up to UTIG data coordinates
    utig_data = pd.read_csv('snr.csv')
    utigX = utig_data['x'].values
    utigY = utig_data['y'].values

    X1, X2 = np.meshgrid(x, utigX)
    Y1, Y2 = np.meshgrid(y, utigY)

    # Set threshold for closeness
    threshold = 2

    # Calculate the distances
    distances = np.sqrt((X1 - X2.T)**2 + (Y1 - Y2.T)**2)

    # Find the closest distances and the corresponding indices
    idx = np.where(distances < threshold)
    i_min, j_min = idx

    # Closest points
    closest_point_set1 = np.column_stack((x[i_min], y[i_min]))
    closest_point_set2 = np.column_stack((utigX[j_min], utigY[j_min]))

    print("Closest points between SNR data and UTIG data:")
    print(closest_point_set1)
    print(closest_point_set2)
else:
    print("No matching .csv and .mat files found or no SNR data to process.")
