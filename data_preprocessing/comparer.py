import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Load the data
cresis_data = pd.read_csv('snr_data.csv')
utig_data = pd.read_csv('snr.csv')

# Extract coordinates and SNR values
cresis_coords = cresis_data[['x', 'y']].values
utig_coords = utig_data[['x', 'y']].values
cresis_snr = cresis_data['snr'].values
utig_snr = utig_data['snr'].values

# Reverse UTIG SNR values by multiplying by -1
utig_snr = utig_snr * -1
utig_data['snr'] = utig_snr

# Build a KD-tree for UTIG data
utig_tree = cKDTree(utig_coords)

# Define a distance threshold for matching points
threshold = 5000
distances, indices = utig_tree.query(cresis_coords, distance_upper_bound=threshold)

# Filter points within the threshold
valid = distances < threshold
cresis_close = cresis_data.iloc[valid]
utig_close = utig_data.iloc[indices[valid]]

# Create a DataFrame with close points and their SNR values
close_points_df = pd.DataFrame({
    'x_cresis': cresis_close['x'],
    'y_cresis': cresis_close['y'],
    'snr_cresis': cresis_close['snr'],
    'x_utig': utig_close['x'].values,
    'y_utig': utig_close['y'].values,
    'snr_utig': utig_close['snr'].values
})

# Save the DataFrame to a CSV file
close_points_csv_path = 'close_points_snr_comparison.csv'
close_points_df.to_csv(close_points_csv_path, index=False)
print(f'Close points with SNR values saved to {close_points_csv_path}')

# Define the Spectral colormap
spectral_cmap = plt.cm.Spectral

# Plotting the data on an Antarctica map
fig, axes = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={'projection': ccrs.SouthPolarStereo()})

# Plot for Cresis data with the Spectral colormap
sc1 = axes[0].scatter(cresis_close['x'], cresis_close['y'], c=cresis_close['snr'], cmap=spectral_cmap, s=20, edgecolor='none', alpha=0.75, vmin=-40, vmax=120, transform=ccrs.SouthPolarStereo())
axes[0].add_feature(cfeature.LAND, edgecolor='black')
axes[0].coastlines(resolution='50m')
axes[0].set_title('Cresis Data')
plt.colorbar(sc1, ax=axes[0], label='Cresis SNR')

# Plot for UTIG data with the Spectral colormap (after reversing SNR values)
sc2 = axes[1].scatter(utig_close['x'], utig_close['y'], c=utig_close['snr'], cmap=spectral_cmap, s=20, edgecolor='none', alpha=0.75, vmin=-40, vmax=120, transform=ccrs.SouthPolarStereo())
axes[1].add_feature(cfeature.LAND, edgecolor='black')
axes[1].coastlines(resolution='50m')
axes[1].set_title('UTIG Data')
plt.colorbar(sc2, ax=axes[1], label='UTIG SNR')

# Adjust layout and display the plot
plt.tight_layout()
plt.show()


