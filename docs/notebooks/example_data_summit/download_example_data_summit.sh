#!/bin/bash

mkdir -p summit

pushd summit

wget -nc https://data.cresis.ku.edu/data/rds/2019_Greenland_P3/CSARP_qlook/20190512_01/Data_20190512_01_057.mat
wget -nc https://data.cresis.ku.edu/data/rds/2019_Greenland_P3/csv_good/20190512_01/Data_20190512_01_057.csv

wget -nc https://data.cresis.ku.edu/data/rds/2019_Greenland_P3/CSARP_qlook/20190512_01/Data_20190512_01_047.mat
wget -nc https://data.cresis.ku.edu/data/rds/2019_Greenland_P3/csv_good/20190512_01/Data_20190512_01_047.csv

wget -nc https://data.cresis.ku.edu/data/rds/2018_Greenland_P3/CSARP_qlook/20180501_01/Data_20180501_01_038.mat
wget -nc https://data.cresis.ku.edu/data/rds/2018_Greenland_P3/csv_good/20180501_01/Data_20180501_01_038.csv

wget -nc https://data.cresis.ku.edu/data/rds/2018_Greenland_P3/CSARP_qlook/20180423_01/Data_20180423_01_052.mat
wget -nc https://data.cresis.ku.edu/data/rds/2018_Greenland_P3/csv_good/20180423_01/Data_20180423_01_052.csv

wget -nc https://data.cresis.ku.edu/data/rds/2018_Greenland_P3/CSARP_qlook/20180423_01/Data_20180423_01_053.mat
wget -nc https://data.cresis.ku.edu/data/rds/2018_Greenland_P3/csv_good/20180423_01/Data_20180423_01_053.csv

popd
