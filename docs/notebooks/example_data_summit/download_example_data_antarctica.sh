#!/bin/bash

mkdir -p antarctica

pushd antarctica

wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/CSARP_qlook/20141115_06/Data_20141115_06_013.mat
wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/csv_good/20141115_06/Data_20141115_06_013_172521.csv

wget -nc https://data.cresis.ku.edu/data/rds/2018_Antarctica_DC8/CSARP_qlook/20181112_04/Data_20181112_04_025.mat
wget -nc https://data.cresis.ku.edu/data/rds/2018_Antarctica_DC8/csv_good/20181112_04/Data_20181112_04_025.csv

wget -nc https://data.cresis.ku.edu/data/rds/2016_Antarctica_DC8/CSARP_qlook/20161115_03/Data_20161115_03_039.mat
wget -nc https://data.cresis.ku.edu/data/rds/2016_Antarctica_DC8/csv_good/20161115_03/Data_20161115_03_039_174840.csv

wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/CSARP_qlook/20141026_07/Data_20141026_07_016.mat
wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/csv_good/20141026_07/Data_20141026_07_016_200939.csv
popd
