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
top_level_dirs = ['2023_Antarctica_BaslerMKB_', '2022_Antarctica_BaslerMKB_', '2018_Antarctica_DC8_', '2018_Antarctica_Ground_', '2019_Antarctica_GV_']
snr_list = []
for top_level_dir in top_level_dirs:
    base_dir = os.path.join(myFolder, top_level_dir)
    if not os.path.isdir(base_dir):
        print(f"Directory does not exist: {base_dir}")
        continue

    # Get a list of CSV and MAT files in the folder
    csv_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(base_dir) for f in filenames if f.endswith('.csv')]
    mat_files = {os.path.splitext(f)[0]: os.path.join(dp, f) for dp, dn, filenames in os.walk(base_dir) for f in filenames if f.endswith('.mat')}


    for csvfullFileName in csv_list:
        name = os.path.splitext(os.path.basename(csvfullFileName))[0]

        if name not in mat_files:  
            print(f'Could not find {name}.mat')
            continue

        csvRelativePath = os.path.relpath(csvfullFileName, myFolder)
        matRelativePath = os.path.relpath(mat_files[name], myFolder)

        # Construct the paths in a platform-independent way
        csvPath = os.path.join('cresis_data', csvRelativePath)
        matPath = os.path.join('cresis_data', matRelativePath)

        try:  # attempt to open mat file
            mat = loadmat(matPath)
            print(f"Using scipy reader for .mat files")
        except NotImplementedError:
            print(f"Using hdf reader for .mat files")
            pass
        except OSError as e:
            print(f"Error opening file '{matPath}': {e}. Moving on to the next file.")
            continue  # next file path

        print(f'Now reading {csvPath} and {matPath}')

        snrs = snrfinder(csvPath, matPath)
        snr_list.append(snrs)


# CRESIS DATA
snr_list = np.vstack(snr_list)

x, y, snr = snr_list[:, 0], snr_list[:, 1], snr_list[:, 2]

df = pd.DataFrame(snr_list, columns=['x', 'y', 'snr'])

# Save the CSV file in a cross-platform way
output_csv_path = os.path.join(myFolder, 'snr_data.csv')
df.to_csv(output_csv_path, index=False)
print(f'Data saved to {output_csv_path}')

# Plot the data
plt.scatter(x, y, c=snr, s=20, cmap='viridis', edgecolor='none', alpha=0.75)
plt.colorbar(label='snr')
plt.show()
