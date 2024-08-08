import numpy as np
import scipy.io
import pandas as pd
import pyproj
import h5py


def ll2ps(lat, lon):
    # Define the polar stereographic projection
    proj_ps = pyproj.Proj(proj='stere', lat_ts=-71, lat_0=-90, lon_0=0, k=1, x_0=0, y_0=0, datum='WGS84')
    x, y = proj_ps(lon, lat)
    return x, y


def load_mat_file(matfile):
    try:
        mat = scipy.io.loadmat(matfile)
        if 'Data' in mat and 'Time' in mat and 'Surface' in mat:
            return mat['Data'], mat['Time'].flatten(), mat['Surface'].flatten()
    except NotImplementedError as e:
        if 'HDF reader for matlab v7.3' in str(e):
            with h5py.File(matfile, 'r') as f:
                Data = f['Data'][()]
                Time = f['Time'][()].flatten()
                Surface = f['Surface'][()].flatten()
                return Data, Time, Surface
    raise ValueError(f"Could not load mat file: {matfile}")


def snrfinder(csv, matfile):
    # Load .mat file
    Data, Time, Surface = load_mat_file(matfile)

    # Load .csv file
    csvdata = pd.read_csv(csv)
    surf = csvdata['SURFACE']
    bott = csvdata['BOTTOM']
    elev = csvdata['ELEVATION']
    thicc = csvdata['THICK']
    lon = csvdata['LON']
    lat = csvdata['LAT']
    e_ice = 3.15

    surf_real = elev - surf
    bott_real = elev - bott
    v = 299792458 / np.sqrt(e_ice)
    propdelayS = surf_real / v
    propdelayB = bott_real / v

    lon_list = []
    lat_list = []
    snr_list = []

    for i in range(len(csvdata)):
        # Check if line has any missing data
        if (surf[i] == -9999 or bott[i] == -9999 or elev[i] == -9999 or thicc[i] == -9999):
            continue

        # Find geometric spreading correction
        geom_spreadingB = (surf[i] + (thicc[i] / np.sqrt(e_ice))) ** 2
        geom_spreadingS = (surf[i]) ** 2

        # Find surface data
        fasttimeS = np.argmin(np.abs(Time - propdelayS[i]))  # Finds surface fasttime
        slowtime = np.argmin(np.abs(Surface - propdelayS[i]))  # Finds slowtime

        surfwatts = np.abs(Data[fasttimeS, slowtime]) * geom_spreadingS  # Pwr w/ geometric spreading correction

        # Find bed data
        fasttimeB = np.argmin(np.abs(Time - propdelayB[i]))  # Finds surface fasttime

        bedwatts = np.abs(Data[fasttimeB, slowtime]) * geom_spreadingB

        # Find SNR using surface and bed power difference
        snr = 10 * np.log10(surfwatts / bedwatts)

        # Add to list of data to plot
        lon_list.append(lon[i])
        lat_list.append(lat[i])
        snr_list.append(snr)

    x, y = ll2ps(lat_list, lon_list)
    values = np.column_stack((x, y, snr_list))  # Returns ps coordinates + snr for future use
    return values