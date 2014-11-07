#!/bin/bash

# creating virtual environment
virtualenv venv
source ~/venv/bin/activate

# installing dependencies
pip install ckanapi
pip install pandas
pip install urllib
pip install scraperwiki

# deactivating
deactivate