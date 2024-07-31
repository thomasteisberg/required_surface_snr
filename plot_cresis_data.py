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
myFolder = filedialog.askdirectory()

# Check to make sure that folder actually exists. Warn user if it doesn't.
if not os.path.isdir(myFolder):
    print(f'Error: The following folder does not exist:\n{myFolder}\nPlease specify a new folder.')
    myFolder = filedialog.askdirectory()
    if myFolder == '':
        # User clicked Cancel
        exit()

# Get a list of all files in the folder with the desired file name pattern
csv_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(myFolder) for f in filenames if f.endswith('.csv')]
mat_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(myFolder) for f in filenames if f.endswith('.mat')]

snr_list = []

for csvfullFileName in csv_list:
    csvFileName = os.path.basename(csvfullFileName)
    name = os.path.splitext(csvFileName)[0]
    matFileName = name + '.mat'
    matfullFileName = os.path.join(myFolder, matFileName)

    if matFileName not in [os.path.basename(f) for f in mat_list]:
        print(f'Could not find {matFileName}')
        continue

    print(f'Now reading {csvFileName} and {matFileName}')

    snrs = snrfinder(csvfullFileName, matfullFileName)
    snr_list.append(snrs)

snr_list = np.vstack(snr_list)

x = snr_list[:, 0]
y = snr_list[:, 1]
snr = snr_list[:, 2]

plt.scatter(x, y, c=snr, s=20, cmap='viridis', edgecolor='k', alpha=0.75)
cb = plt.colorbar()
cb.set_label('snr')
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
