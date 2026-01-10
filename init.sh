#!/bin/bash
# Create the environment with Python 3.10
conda create -n c4u_scraper python=3.10 -y

conda init
# Activate the environment
conda activate c4u_scraper
pip install pandas
pip install beautifulsoup4
