#!/bin/bash

#
#SBATCH --job-name=raw_to_snr
#
#SBATCH --partition=serc
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=32G

date

source /home/users/teisberg/.bashrc
mamba activate rssnr

cd /oak/stanford/groups/dustinms/thomas/repos/required_surface_snr/data_preprocessing/
python raw_to_snr.py --dataset Greenland --output snr_data_cresis_gis.csv
python raw_to_snr.py --dataset Antarctica --output snr_data_cresis_ais.csv

date

