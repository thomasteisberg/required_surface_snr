#!/bin/bash

mkdir -p antarctica

pushd antarctica

wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/CSARP_qlook/20141115_05/Data_20141115_05_004.mat
wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/csv_good/20141115_05/Data_20141115_05_004_160511.csv

wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/CSARP_qlook/20141115_06/Data_20141115_06_010.mat
wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/csv_good/20141115_06/Data_20141115_06_010_170655.csv

wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/CSARP_qlook/20141115_06/Data_20141115_06_011.mat
wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/csv_good/20141115_06/Data_20141115_06_011_171320.csv

wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/CSARP_qlook/20141115_06/Data_20141115_06_012.mat
wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/csv_good/20141115_06/Data_20141115_06_012_171915.csv

wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/CSARP_qlook/20141115_06/Data_20141115_06_013.mat
wget -nc https://data.cresis.ku.edu/data/rds/2014_Antarctica_DC8/csv_good/20141115_06/Data_20141115_06_013_172521.csv

wget -nc https://data.cresis.ku.edu/data/rds/2018_Antarctica_DC8/CSARP_qlook/20181112_01/Data_20181112_01_026.mat
wget -nc https://data.cresis.ku.edu/data/rds/2018_Antarctica_DC8/csv_good/20181112_01/Data_20181112_01_026.csv

popd
