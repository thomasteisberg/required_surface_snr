import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Hide the root window of Tkinter
root = Tk()
root.withdraw()

# Specify the folder where the SNR data file is located
myFolder = filedialog.askdirectory()

# Load the CSV file
csv_file_path = os.path.join(myFolder, 'snr_data.csv')

if not os.path.isfile(csv_file_path):
    print(f'Error: The following file does not exist:\n{csv_file_path}')
    exit()

df = pd.read_csv(csv_file_path)

x, y, snr = df['x'], df['y'], df['snr']

# Define the same Polar Stereographic projection used in ll2ps
proj_ps = ccrs.Stereographic(central_latitude=-90, true_scale_latitude=-71)

# Create a plot with Cartopy using the same Polar Stereographic projection
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': proj_ps})

# Add coastlines and land features with higher resolution
ax.coastlines(resolution='50m')
ax.add_feature(cfeature.LAND, edgecolor='black')

# Plot the data on the map
scatter = ax.scatter(x, y, c=snr, s=20, cmap='viridis', edgecolor='none', alpha=0.75, transform=proj_ps)

# Add a colorbar for the SNR values
plt.colorbar(scatter, ax=ax, label='snr')

# Set extent to focus more closely on Antarctica (adjust if necessary)
ax.set_extent([-2500000, 2500000, -2500000, 2500000], crs=proj_ps)

# Display the plot
plt.show()


