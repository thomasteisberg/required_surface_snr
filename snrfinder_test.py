import numpy as np
from scipy.io import loadmat
import pandas as pd
import pyproj
import h5py


def ll2ps(lat, lon):
    # Define the polar stereographic projection
    # For example, EPSG:3031 is commonly used for the Antarctic region
    proj_ps = pyproj.Proj(proj='stere', lat_ts=-71, lat_0=-90, lon_0=0, k=1, x_0=0, y_0=0, datum='WGS84')
    x, y = proj_ps(lon, lat)
    return x, y


def snrfinder(csv, matfile):
    sci = False
    hdf = False

    # Load .mat file
    try:  # attempt to open with scipy
        mat = loadmat(matfile)
        Data = np.array(mat['Data'], dtype=np.float32)  # Explicitly set dtype to save memory
        Data = np.transpose(Data)  # Transpose to match MATLAB indexing if necessary
        Time = np.array(mat['Time'], dtype=np.float32)
        LonMat = np.array(mat['Longitude'], dtype=np.float32)
        LatMat = np.array(mat['Latitude'], dtype=np.float32)
        sci = True
    except NotImplementedError:  # use hdf reader if scipy doesn't work
        with h5py.File(matfile, 'r') as mat:
            Data = np.array(mat['Data'], dtype=np.float32)
            Time = np.array(mat['Time'], dtype=np.float32)
            LonMat = np.array(mat['Longitude'], dtype=np.float32)
            LatMat = np.array(mat['Latitude'], dtype=np.float32)
            # No transpose needed here, assuming HDF5 files are structured correctly
        hdf = True

    # Load .csv file
    csvdata = pd.read_csv(csv)
    surf = csvdata['SURFACE'].values.astype(np.float32)
    bott = csvdata['BOTTOM'].values.astype(np.float32)
    elev = csvdata['ELEVATION'].values.astype(np.float32)
    thicc = csvdata['THICK'].values.astype(np.float32)
    csv_lon = csvdata['LON'].values.astype(np.float32)
    csv_lat = csvdata['LAT'].values.astype(np.float32)

    e_ice = 3.15

    # Convert latitude and longitude to PS coordinates
    xMat, yMat = ll2ps(LatMat, LonMat)
    xCSV, yCSV = ll2ps(csv_lat, csv_lon)

    x_list = []
    y_list = []
    snr_list = []

    # Calculate Propagation Delays
    v = 299792458 / np.sqrt(e_ice)
    propdelayS = (surf / 299792458) * 2
    propdelayB = (((bott - surf) / v) * 2) + propdelayS

    for csv_i in range(len(xCSV)):  # loop through coordinates in the .csv file
        x = xCSV[csv_i]
        y = yCSV[csv_i]

        # Find the squared Euclidean distance between the current CSV point and all points in the mat file
        distances = (xMat - x) ** 2 + (yMat - y) ** 2

        # Find the index of the closest point in the mat file
        mat_i = np.argmin(distances)

        # Check if line has any missing data
        if (surf[csv_i] == -9999 or bott[csv_i] == -9999 or elev[csv_i] == -9999 or thicc[csv_i] == -9999):
            continue

        # Find fasttimes
        fasttimeS = np.argmin(np.abs(Time - propdelayS[csv_i]))  # Finds surface fasttime
        fasttimeB = np.argmin(np.abs(Time - propdelayB[csv_i]))  # Finds bed fasttime

        # Find geometric spreading correction
        geom_spreadingB = (surf[csv_i] + (thicc[csv_i] / np.sqrt(e_ice))) ** 2
        geom_spreadingS = (surf[csv_i]) ** 2

        # Find reflected power in data matrix (watts), multiply by geom spreading
        surfwatts = np.abs(Data[mat_i, fasttimeS]) * geom_spreadingS  # Pwr w/ geometric spreading correction
        bedwatts = np.abs(Data[mat_i, fasttimeB]) * geom_spreadingB

        # Calculate SNR
        snr = 10 * np.log10(surfwatts / bedwatts)

        # Add to list of data to plot
        x_list.append(x)
        y_list.append(y)
        snr_list.append(snr)

    # Free up memory by explicitly deleting large arrays that are no longer needed
    del Data, Time, LonMat, LatMat, xMat, yMat, xCSV, yCSV, surf, bott, elev, thicc

    x, y = ll2ps(np.array(y_list), np.array(x_list))

    values = np.column_stack((x, y, snr_list))  # Returns PS coordinates + SNR for future use
    return values
