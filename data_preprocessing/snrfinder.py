import numpy as np
from scipy.io import loadmat
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import h5py
import scipy.constants

epsg_3031 = pyproj.Proj("EPSG:3031")
epsg_3413 = pyproj.Proj("EPSG:3413")
#epsg_3031 = pyproj.Proj(proj='stere', lat_ts=-71, lat_0=-90, lon_0=0, k=1, x_0=0, y_0=0, datum='WGS84')
#epsg_3413 = pyproj.Proj(proj='stere', lat_ts=70, lat_0=90, lon_0=-45, k=1, x_0=0, y_0=0, datum='WGS84')
#proj = crs_3413 = ccrs.Stereographic(central_latitude=90, central_longitude=-45, true_scale_latitude=70) # All Greenland data will be projected (if needed) to this

def ll2ps(lat, lon, proj_ps=epsg_3031):
    # Define the polar stereographic projection
    # For example, EPSG:3031 is commonly used for the Antarctic region
    #proj_ps = pyproj.Proj(proj='stere', lat_ts=-71, lat_0=-90, lon_0=0, k=1, x_0=0, y_0=0, datum='WGS84')
    x, y = proj_ps(lon, lat)
    return x, y

def calculate_rssnr(csv_path, mat_path, ice_sheet='antarctica', save_plot=True, plot_path=None):
    e_ice = 3.15
    vel_ice = scipy.constants.c / np.sqrt(e_ice)

    if ice_sheet == 'greenland':
        proj_ps = epsg_3413
    elif ice_sheet == 'antarctica':
        proj_ps = epsg_3031
    else:
        raise ValueError("Invalid ice sheet specified. Use 'greenland' or 'antarctica'.")

    # Load and sanity check data
    sci = False
    hdf = False

    #Load .mat file
    try: # attempt to open with scipy
        mat = loadmat(mat_path)
        mat["Data"] = mat["Data"].T
        sci = True
    except NotImplementedError: #use hdf reader if scipy doesn't work
        mat = h5py.File(mat_path, 'r')
        hdf = True

    # Load .csv file
    csvdata = pd.read_csv(csv_path, na_values=[-9999, "-9999"])

    csv_time_rel = np.array(csvdata['UTCTIMESOD'] - csvdata['UTCTIMESOD'].iloc[0])
    mat_time_rel = np.squeeze(mat['GPS_time'] - mat['GPS_time'][0][0])

    # Sanity checks on time
    if np.any(np.diff(csv_time_rel) < 0):
        print("CSV time is not monotonic")
        raise ValueError("CSV time is not monotonic")
    if np.any(np.diff(mat_time_rel) < 0):
        print("MAT time is not monotonic")
        raise ValueError("MAT time is not monotonic")
    if np.abs(csv_time_rel[-1] - mat_time_rel[-1]) > 3:
        print(f"CSV and MAT timespans differ by more than 3 seconds. Max diff: {np.max(np.abs(csv_time_rel - mat_time_rel))} seconds")
        raise ValueError("CSV and MAT timespans differ by more than 3 seconds")

    decimation = np.ceil(len(csv_time_rel) / len(mat_time_rel)).astype(int)
    #print(f"Decimation factor: {decimation}")

    csvdata = csvdata[::decimation].dropna()

    # Extract surface and bed power information

    mat_slow_idx = []
    mat_surf_idx = []
    mat_bott_idx = []
    surface_pwr_db = []
    bottom_pwr_db = []
    rssnr_db = []

    fasttime_mat = np.squeeze(mat['Time'])

    def pick_power(slowtime_idx, fasttime_idx, fasttime_half_width_idx=2):
        start_idx = np.maximum(0, fasttime_idx - fasttime_half_width_idx)
        end_idx = np.minimum(len(fasttime_mat)-1, fasttime_idx + fasttime_half_width_idx)
        return np.max(mat['Data'][slowtime_idx, start_idx:end_idx])

    # Loop through each row in the CSV file
    for i, row in csvdata.iterrows():
        slowtime_idx = np.argmin(np.abs(csv_time_rel[i] - mat_time_rel))
        
        surface_fasttime = row['SURFACE'] / (scipy.constants.c/2)
        bottom_fasttime = surface_fasttime + (row['THICK'] / (vel_ice/2))

        surf_idx = np.argmin(np.abs(surface_fasttime - mat['Time']))
        bot_idx = np.argmin(np.abs(bottom_fasttime - mat['Time']))
        

        # Find surface and bed power
        surf_pwr = pick_power(slowtime_idx, surf_idx)
        bot_pwr = pick_power(slowtime_idx, bot_idx)

        # Calculate geometric spreading corrections
        geom_spreading_surf = row['SURFACE']**2
        geom_spreading_bed = (row['SURFACE'] + (row['THICK'] / np.sqrt(e_ice)))**2

        rssnr_lin = surf_pwr * geom_spreading_surf / (bot_pwr * geom_spreading_bed)

        # Add results to lists
        mat_slow_idx.append(slowtime_idx)
        mat_surf_idx.append(surf_idx)
        mat_bott_idx.append(bot_idx)
        surface_pwr_db.append(10 * np.log10(surf_pwr))
        bottom_pwr_db.append(10 * np.log10(bot_pwr))
        rssnr_db.append(10 * np.log10(rssnr_lin))

    df_res = pd.DataFrame({
        'mat_slow_idx': mat_slow_idx,
        'mat_surf_idx': mat_surf_idx,
        'mat_bott_idx': mat_bott_idx,
        'surface_pwr_db': surface_pwr_db,
        'bottom_pwr_db': bottom_pwr_db,
        'snr': rssnr_db,
        'surface': csvdata['SURFACE'],
        'thickness': csvdata['THICK'],
        'bottom': csvdata['BOTTOM'],
        'latitude': csvdata['LAT'],
        'longitude': csvdata['LON'],
        })

    # Convert lat/lon to polar stereographic coordinates
    x, y = ll2ps(df_res['latitude'], df_res['longitude'], proj_ps=proj_ps)
    df_res['x'] = x
    df_res['y'] = y

    # Optionally, produce a debugging plot
    if save_plot:
        fig, (ax, ax_pwr, ax_rssnr) = plt.subplots(3, 1, figsize=(12, 9), sharex=True, gridspec_kw={'height_ratios': [2, 1, 1]})

        # Plot radargram
        X, Y = np.meshgrid(np.arange(len(np.squeeze(mat["GPS_time"]))), np.arange(len(np.squeeze(mat["Time"]))))
        ax.pcolormesh(X, Y, 10*np.log10(np.abs(mat["Data"])).T, cmap='gray', shading='nearest')
        ax.set_ylim(1.2*np.max(df_res['mat_bott_idx']), 0)
        ax.set_ylabel('Fast Time Index')

        # Plot picks on radargram
        ax.plot(df_res['mat_slow_idx'], df_res['mat_surf_idx'], '--', markersize=0.1, label='Surface Picks')
        ax.plot(df_res['mat_slow_idx'], df_res['mat_bott_idx'], '--', markersize=0.1, label='Bottom Picks')
        ax.legend()

        # Plot surface and bed power
        ax_pwr.plot(df_res['mat_slow_idx'], df_res['surface_pwr_db'], label='Surface Power')
        ax_pwr.plot(df_res['mat_slow_idx'], df_res['bottom_pwr_db'], label='Bed Power')
        ax_pwr.set_ylabel('Power [dB]')
        ax_pwr.legend()
        ax_pwr.grid()

        # Plot RSSNR
        ax_rssnr.plot(df_res['mat_slow_idx'], df_res['snr'], 'k-', label='RSSNR')
        ax_rssnr.plot(df_res['mat_slow_idx'], df_res['surface_pwr_db'] - df_res['bottom_pwr_db'], c='gray', linestyle=":", label='Surface - Bed')
        ax_rssnr.set_ylabel('Power [dB]')
        ax_rssnr.set_xlabel('Slow Time Index')
        ax_rssnr.legend()
        ax_rssnr.grid()

        ax.set_title(f"{mat_path}")
        
        if plot_path is None:
            plot_path = f"{csv_path}.png"
        print(f"Saving plot to {plot_path}")
        fig.savefig(plot_path)
        plt.close(fig)
    
    return df_res
