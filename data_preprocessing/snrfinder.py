import numpy as np
from scipy.io import loadmat
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import h5py

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

def snrfinder(csv, matfile, ice_sheet='antarctica'):

    if ice_sheet == 'greenland':
        proj_ps = epsg_3413
    elif ice_sheet == 'antarctica':
        proj_ps = epsg_3031
    else:
        raise ValueError("Invalid ice sheet specified. Use 'greenland' or 'antarctica'.")

    sci = False
    hdf = False
    #Load .mat file
    try: #attempt to open with scipy
        mat = loadmat(matfile)
        Data = mat.get('Data')
        Data = np.array(Data)
        Time = mat.get('Time')
        Time = np.array(Time)
        Surface = mat.get('Surface')
        Surface = np.array(Surface)
        sci = True
    except NotImplementedError: #use hdf reader if scipy doesn't work
        mat = h5py.File(matfile, 'r')
        Data = mat.get('Data')
        Data = np.array(Data)
        Time = mat.get('Time')
        Time = np.array(Time)
        Surface = mat.get('Surface')
        Surface = np.array(Surface)
        hdf = True

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

        # Find bed data
        fasttimeB = np.argmin(np.abs(Time - propdelayB[i]))  # Finds surface fasttime

        if (hdf): # FLIP THE INDEXES INTO THE DATA MATRIX
            surfwatts = np.abs(Data[slowtime, fasttimeS]) * geom_spreadingS  # Pwr w/ geometric spreading correction
            bedwatts = np.abs(Data[slowtime, fasttimeB]) * geom_spreadingB
        else: # SAME AS MATLAB INDEXING
            surfwatts = np.abs(Data[fasttimeS, slowtime]) * geom_spreadingS
            bedwatts = np.abs(Data[fasttimeB, slowtime]) * geom_spreadingB

        # Find SNR using surface and bed power difference
        snr = 10 * np.log10(surfwatts / bedwatts)

        # Add to list of data to plot
        lon_list.append(lon[i])
        lat_list.append(lat[i])
        snr_list.append(snr)

    x, y = ll2ps(lat_list, lon_list, proj_ps=proj_ps)  # Convert lat/lon to polar stereographic coordinates
    """ plt.scatter(x, y, 20, snr_list, cmap='viridis')
    cb = plt.colorbar()
    cb.set_label('snr')
    plt.show() """

    values = np.column_stack((x, y, snr_list))  # Returns ps coordinates + snr for future use
    return values

#snrfinder(r'cresis_data\2023_Antarctica_BaslerMKB_\csv_20240107_01_\Data_20240107_01_028.csv', r'cresis_data\2023_Antarctica_BaslerMKB_\CSARP_qlook_20240107_01_\Data_20240107_01_028.mat')
#snrfinder('Data_20240107_01_028.csv', 'Data_20240107_01_028.mat')
#snrfinder(r'cresis_data\2018_Antarctica_DC8_\csv_20181010_01_\Data_20181010_01_001.csv', r'cresis_data\2018_Antarctica_DC8_\CSARP_qlook_20181010_01_\Data_20181010_01_001.mat') # uses hdf reader, flips data matrix from MatLab version
#snrfinder(r'cresis_data\2023_Antarctica_BaslerMKB_\csv_20240104_01_\Data_20240104_01_029.csv', r'cresis_data\2023_Antarctica_BaslerMKB_\CSARP_qlook_20240104_01_\Data_20240104_01_029.mat') # uses scipy reader, matrix dimensions are the same as in Matlab
