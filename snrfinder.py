import numpy as np
from scipy.io import loadmat
import pandas as pd
import matplotlib.pyplot as plt
import pyproj
import h5py

def ll2ps(lat, lon):
    # Define the polar stereographic projection
    # For example, EPSG:3031 is commonly used for the Antarctic region
    proj_ps = pyproj.Proj(proj='stere', lat_ts=-71, lat_0=-90, lon_0=0, k=1, x_0=0, y_0=0, datum='WGS84')
    x, y = proj_ps(lon, lat)
    return x, y

#--------------------------snrfinder revision---------------------------------------------------------------------------------------------
def radargram(datafile):
    try: #attempt to open with scipy
        mat = loadmat(datafile)
        Data = mat.get('Data')
        #Data = np.transpose(Data)
    except NotImplementedError: #use hdf reader if scipy doesn't work
        mat = h5py.File(datafile, 'r')
        Data = mat.get('Data')
        Data = np.transpose(Data)
    
    d = 10 * np.log10(np.abs(Data))
    
    plt.imshow(np.abs(d), cmap='gray')
    #plt.show()

def find_closest_point(x, y, x_points, y_points):
    
    # Calculate squared Euclidean distance to avoid sqrt for efficiency
    distances = (x_points - x)**2 + (y_points - y)**2
    # Find the index of the minimum distance
    index = np.argmin(distances)
    #closest_point = [x_points[index], y_points[index]]

    return index

def snrfinder(csv, matfile):
    sci = False
    hdf = False
    #Load .mat file
    try: #attempt to open with scipy
        mat = loadmat(matfile)
        Data = np.array(mat['Data'], dtype=np.float32)  # Explicitly set dtype to save memory
        Data = np.transpose(Data)  # Transpose to match MATLAB indexing if necessary
        Time = np.array(mat['Time'], dtype=np.float32)
        LonMat = np.array(mat['Longitude'], dtype=np.float32)
        LonMat = np.transpose(LonMat)
        LatMat = np.array(mat['Latitude'], dtype=np.float32)
        LatMat = np.transpose(LatMat)
        sci = True
    except NotImplementedError: #use hdf reader if scipy doesn't work
        with h5py.File(matfile, 'r') as mat:
            Data = np.array(mat['Data'], dtype=np.float32)
            Time = np.array(mat['Time'], dtype=np.float32)
            LonMat = np.array(mat['Longitude'], dtype=np.float32)
            LatMat = np.array(mat['Latitude'], dtype=np.float32)
            # No transpose needed here, assuming HDF5 files are structured correctly
        hdf = True

    #radargram(matfile)
    # Load .csv file
    csvdata = pd.read_csv(csv)
    surf = csvdata['SURFACE'].values.astype(np.float32)
    bott = csvdata['BOTTOM'].values.astype(np.float32)
    elev = csvdata['ELEVATION'].values.astype(np.float32)
    thicc = csvdata['THICK'].values.astype(np.float32)
    csv_lon = csvdata['LON'].values.astype(np.float32)
    csv_lat = csvdata['LAT'].values.astype(np.float32)

    e_ice = 3.15

    # convert latitude and longitude to PS coordinates
    [xMat, yMat] = ll2ps(LatMat, LonMat)
    [xCSV, yCSV] = ll2ps(csv_lat, csv_lon)

    """ csv_i_list = []
    mat_i_list = [] """
    x_list = []
    y_list = []
    snr_list = []

    # Calculate Propogation Delays
    v = 299792458 / np.sqrt(e_ice)
    propdelayS = (surf / 299792458) * 2
    propdelayB = (((bott - surf) / v) * 2)  + propdelayS

    for slowtime in range(len(xMat)): # loop through coordinates in the .mat file
        x = xMat[slowtime]
        y = yMat[slowtime]

        # find closest point in .csv file
        csv_i = find_closest_point(x, y, xCSV, yCSV)

        # Check if line has any missing data
        if (surf[csv_i] == -9999 or bott[csv_i] == -9999 or elev[csv_i] == -9999 or thicc[csv_i] == -9999):
            continue

        # plot .csv index vs .mat index
        """ csv_i_list.append(csv_i)
        mat_i_list.append(mat_i) """

        # find fasttimes
        fasttimeS = np.argmin(np.abs(Time - propdelayS[csv_i]))  # Finds surface fasttime
        fasttimeB = np.argmin(np.abs(Time - propdelayB[csv_i]))  # Finds bed fasttime

        # Find geometric spreading correction
        geom_spreadingB = (surf[csv_i] + (thicc[csv_i] / np.sqrt(e_ice))) ** 2
        geom_spreadingS = (surf[csv_i]) ** 2

        # Find reflected power in data matrix (watts), multiply by geom spreading
        surfwatts = np.abs(Data[slowtime, fasttimeS]) * geom_spreadingS  # Pwr w/ geometric spreading correction
        bedwatts = np.abs(Data[slowtime, fasttimeB]) * geom_spreadingB

        # Plot slowtime and fasttime on radargram(for debugging purposes)
        """plt.scatter(slowtime, fasttimeS,      color='red', s=20)
        plt.scatter(slowtime, fasttimeB,      color='blue', s=20)"""

        # calculate required surface snr (dB)
        snr = 10 * np.log10(surfwatts / bedwatts)

        # Add to list of data to plot 
        x_list.append(x)
        y_list.append(y)
        snr_list.append(snr)

    # Free up memory by explicitly deleting large arrays that are no longer needed
    del Data, Time, LonMat, LatMat, xMat, yMat, xCSV, yCSV, surf, bott, elev, thicc

    #plt.show()

    values = np.column_stack((x_list, y_list, snr_list))  # Returns ps coordinates + snr for future use
    return values


#snrfinder('cresis_data/2023_Antarctica_BaslerMKB_/csv_20240104_01_/Data_20240104_01_029.csv', 'cresis_data/2023_Antarctica_BaslerMKB_/CSARP_qlook_20240104_01_/Data_20240104_01_029.mat') # uses scipy reader, matrix dimensions are the same as in Matlab
#snrfinder(r'cresis_data\2018_Antarctica_DC8_\csv_20181010_01_\Data_20181010_01_001.csv', r'cresis_data\2018_Antarctica_DC8_\CSARP_qlook_20181010_01_\Data_20181010_01_001.mat') # uses hdf reader, flips data matrix from MatLab version
#radargram('cresis_data/2018_Antarctica_DC8_/CSARP_qlook_20181010_01_/Data_20181010_01_001.mat')
#radargram(r'cresis_data\2023_Antarctica_BaslerMKB_\CSARP_qlook_20240104_01_\Data_20240104_01_029.mat')
#snrfinder(r'cresis_data\2023_Antarctica_BaslerMKB_\csv_20231209_01_\Data_20231209_01_009.csv', r'cresis_data\2023_Antarctica_BaslerMKB_\CSARP_qlook_20231209_01_\Data_20231209_01_009.mat')
#snrfinder(r'cresis_data\2023_Antarctica_BaslerMKB_\csv_20231221_01_\Data_20231221_01_021.csv', r'cresis_data\2023_Antarctica_BaslerMKB_\CSARP_qlook_20231221_01_\Data_20231221_01_021.mat')
