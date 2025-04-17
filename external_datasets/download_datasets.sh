#!/bin/bash

echo "A (free) NASA Earthdata login is required to download some of these datasets. Please enter your Earthdata credentials when prompted below."
read -p "NASA Earthdata Username: " NASA_EARTHDATA_USER
read -s -p "NASA Earthdata Password (not shown): " NASA_EARTHDATA_PASS

echo ""

# Ice Thickness - Antarctica
# https://nsidc.org/data/nsidc-0756/versions/3
wget -nc --http-user=$NASA_EARTHDATA_USER --http-password=$NASA_EARTHDATA_PASS https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0756.003/1970.01.01/BedMachineAntarctica-v3.nc
# Ice Thickness - Greenland
# https://nsidc.org/data/idbmg4/versions/5
wget -nc --http-user=$NASA_EARTHDATA_USER --http-password=$NASA_EARTHDATA_PASS https://n5eil01u.ecs.nsidc.org/ICEBRIDGE/IDBMG4.005/1993.01.01/BedMachineGreenland-v5.nc

# Ice Velocity - Antarctica
# https://nsidc.org/data/nsidc-0754/versions/1
wget -nc --http-user=$NASA_EARTHDATA_USER --http-password=$NASA_EARTHDATA_PASS https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0754.001/1996.01.01/antarctic_ice_vel_phase_map_v01.nc
# Ice Velocity - Greenland
# ITS_LIVE Greenland velocity mosaic
wget -nc https://its-live-data.s3.amazonaws.com/velocity_mosaic/v2/static/ITS_LIVE_velocity_120m_RGI05A_0000_v02.nc


# Alternative Greenland Ice Velocity -- not using
# # https://nsidc.org/data/nsidc-0670/versions/1
# wget -nc --http-user=$NASA_EARTHDATA_USER --http-password=$NASA_EARTHDATA_PASS https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0670.001/1995.12.01/greenland_vel_mosaic250_vx_v1.tif
# wget -nc --http-user=$NASA_EARTHDATA_USER --http-password=$NASA_EARTHDATA_PASS https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0670.001/1995.12.01/greenland_vel_mosaic250_vy_v1.tif
# wget -nc --http-user=$NASA_EARTHDATA_USER --http-password=$NASA_EARTHDATA_PASS https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0670.001/1995.12.01/greenland_vel_mosaic250_ex_v1.tif
# wget -nc --http-user=$NASA_EARTHDATA_USER --http-password=$NASA_EARTHDATA_PASS https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0670.001/1995.12.01/greenland_vel_mosaic250_ey_v1.tif