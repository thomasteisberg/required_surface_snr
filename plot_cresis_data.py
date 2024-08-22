import os
from tkinter import filedialog, Tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from snrfinder import snrfinder
from scipy.io import loadmat

# Hide the root window of Tkinter
root = Tk()
root.withdraw()

# Specify the folder where the files live
myFolder = filedialog.askdirectory()

# Check if the folder exists
while not os.path.isdir(myFolder):
    print(f'Error: The following folder does not exist:\n{myFolder}\nPlease specify a new folder.')
    myFolder = filedialog.askdirectory()
    if myFolder == '':
        exit()  # User clicked Cancel

# Top-level directories to process
top_level_dirs = [
    '2023_Antarctica_BaslerMKB_', '2022_Antarctica_BaslerMKB_', 
    '2018_Antarctica_DC8_', '2018_Antarctica_Ground_', '2019_Antarctica_GV_'
]

output_csv_path = 'snr_data_complete.csv'
with open(output_csv_path, 'w') as outfile:
    outfile.write('x,y,snr\n')  # Write the header

    for top_level_dir in top_level_dirs:
        base_dir = os.path.join(myFolder, top_level_dir)
        if not os.path.isdir(base_dir):
            print(f"Directory does not exist: {base_dir}")
            continue

        # Get a list of CSV and MAT files in the folder
        mat_files = {
            os.path.splitext(f)[0]: os.path.join(dp, f) 
            for dp, dn, filenames in os.walk(base_dir) 
            for f in filenames if f.endswith('.mat')
        }

        csv_list = [
            os.path.join(dp, f) 
            for dp, dn, filenames in os.walk(base_dir) 
            for f in filenames if f.endswith('.csv')
        ]

        for csvfullFileName in csv_list:
            name = os.path.splitext(os.path.basename(csvfullFileName))[0]

            if name not in mat_files:
                print(f'Could not find {name}.mat')
                continue

            csvRelativePath = os.path.relpath(csvfullFileName, myFolder)
            matRelativePath = os.path.relpath(mat_files[name], myFolder)

            csvPath = 'cresis_data\\' + csvRelativePath
            matPath = 'cresis_data\\' + matRelativePath

            """ try:
                mat = loadmat(matPath)
            except NotImplementedError:
                pass
            except OSError as e:
                print(f"Error opening file '{matPath}': {e}. Moving on to next file.")
                continue # next file path """

            print(f'Now reading {csvPath} and {matPath}')

            snrs = snrfinder(csvPath, matPath)

            # Save results incrementally
            np.savetxt(outfile, snrs, delimiter=',', fmt='%f')

# CRESIS DATA   
snr_data = np.loadtxt(output_csv_path, delimiter=',', skiprows=1)
x, y, snr = snr_data[:, 0], snr_data[:, 1], snr_data[:, 2]

plt.scatter(x, y, c=snr, s=20, cmap='viridis', edgecolor='none', alpha=0.75)
plt.colorbar(label='snr')
plt.show()
