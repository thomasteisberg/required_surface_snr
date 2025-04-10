#!/bin/bash
#
#SBATCH --job-name=cresis_antarctica
#SBATCH --partition=serc
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G
#SBATCH -C CLASS:SH3_CBASE|CLASS:SH3_CPERF
#SBATCH --array=2018-2023
#SBATCH --output=slurm-cresis-antarctica-%A_%a.out

# Get current date and hostname for logging
date
hostname

# Activate environment
source /home/users/teisberg/.bashrc
conda activate rssnr

# Go to project directory
cd /oak/stanford/groups/dustinms/thomas/repos/required_surface_snr/data_preprocessing

# Run the Python script for the specific year based on array task ID
python data_scrapper.py --year=${SLURM_ARRAY_TASK_ID} --dataset Antarctica

hostname
date

