import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
cresis_data = pd.read_csv('snr_data.csv')
utig_data = pd.read_csv('snr.csv')
cresis_coords = cresis_data[['x', 'y']].values
utig_coords = utig_data[['x', 'y']].values
cresis_snr = cresis_data['snr'].values
utig_snr = utig_data['snr'].values
""" utig_tree = cKDTree(utig_coords)
threshold = 5000
distances, indices = utig_tree.query(cresis_coords, distance_upper_bound=threshold)
valid = distances < threshold
cresis_close = cresis_data.iloc[valid]
utig_close = utig_data.iloc[indices[valid]]
snr_diff = np.abs(cresis_close['snr'].values - utig_close['snr'].values)
close_points_df = pd.DataFrame({
    'x_cresis': cresis_close['x'],
    'y_cresis': cresis_close['y'],
    'snr_cresis': cresis_close['snr'],
    'x_utig': utig_close['x'].values,
    'y_utig': utig_close['y'].values,
    'snr_utig': utig_close['snr'].values
}) """

utig_tree = cKDTree(utig_coords)
distances, indices = utig_tree.query(cresis_coords)
utig_closest_points = utig_coords[indices]
utig_closest_snr = utig_snr[indices]
closest_points_df = pd.DataFrame({ 'x_cresis': cresis_coords[:, 0], 'y_cresis': cresis_coords[:, 1], 'snr_cresis': cresis_snr, 'x_utig_closest': utig_closest_points[:, 0], 'y_utig_closest': utig_closest_points[:, 1], 'snr_utig_closest': utig_closest_snr })

close_points_csv_path = 'close_points_snr_comparison.csv'
closest_points_df.to_csv(close_points_csv_path, index=False)
print(f'Close points with SNR values saved to {close_points_csv_path}')
plt.figure(figsize=(12, 6))
# Plot for Cresis data
plt.subplot(1, 2, 1)
plt.scatter(cresis_coords['x'], cresis_coords['y'], c=cresis_snr['snr'], cmap='viridis', s=20, edgecolor='none', alpha=0.75)
plt.colorbar(label='Cresis SNR')
plt.title('Cresis Data')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
# Plot for UTIG data
plt.subplot(1, 2, 2)
plt.scatter(utig_closest_points['x'], utig_closest_points['y'], c=utig_closest_snr['snr'], cmap='viridis', s=20, edgecolor='none', alpha=0.75)
plt.colorbar(label='UTIG SNR')
plt.title('UTIG Data')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.tight_layout()
plt.show()