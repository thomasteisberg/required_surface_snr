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

# Get a list of CSV and MAT files in the folder
csv_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(myFolder) for f in filenames if f.endswith('.csv')]
mat_files = {os.path.splitext(f)[0]: os.path.join(dp, f) for dp, dn, filenames in os.walk(myFolder) for f in filenames if f.endswith('.mat')}

snr_list = []

for csvfullFileName in csv_list:
    name = os.path.splitext(os.path.basename(csvfullFileName))[0]

    if name not in mat_files:
        print(f'Could not find {name}.mat')
        continue

    csvRelativePath = os.path.relpath(csvfullFileName, myFolder)
    matRelativePath = os.path.relpath(mat_files[name], myFolder)

    csvPath = 'cresis_data\\2023_Antarctica_BaslerMKB_\\' + csvRelativePath
    matPath = 'cresis_data\\2023_Antarctica_BaslerMKB_\\' + matRelativePath

    try: #attempt to open mat file
        mat = loadmat(matPath)
    except OSError as e:
        print(f"Error opening file '{matPath}': {e}. Moving on to next file.")
        continue # next file path

    print(f'Now reading {csvPath} and {matPath}')

    snrs = snrfinder(csvPath, matPath)
    snr_list.append(snrs)
# CRESIS DATA   
snr_list = np.vstack(snr_list)

x, y, snr = snr_list[:, 0], snr_list[:, 1], snr_list[:, 2]

df = pd.DataFrame(snr_list, columns=['x', 'y', 'snr'])
output_csv_path = 'snr_data.csv'
df.to_csv(output_csv_path, index=False)
print(f'Data saved to {output_csv_path}')

plt.scatter(x, y, c=snr, s=20, cmap='viridis', edgecolor='none', alpha=0.75)
plt.colorbar(label='snr')
plt.show()

# -------------------------------
# Check if any coordinates are close to UTIG data coordinates
""" utig_data = pd.read_csv('snr.csv')
utigX, utigY = utig_data['x'].values, utig_data['y'].values
utig_snr = utig_data['snr'].values

# Calculate the distances and find close points
threshold = 5000
distances = np.sqrt((x[:, np.newaxis] - utigX)**2 + (y[:, np.newaxis] - utigY)**2)

# Find points within the threshold
i_min, j_min = np.where(distances < threshold)

# Closest points
closest_point_set1 = np.column_stack((x[i_min], y[i_min], snr[i_min]))
closest_point_set2 = np.column_stack((utigX[j_min], utigY[j_min], utig_snr[j_min])) """
#np.row_stack((closest_point_set1, closest_point_set2))
