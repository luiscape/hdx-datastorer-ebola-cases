#!/bin/bash

# activating the virtualenv
source ~/venv/bin/activate

# creating / updating datastore
python ~/tool/code/create-datastore.py f48a3cf9-110e-4892-bedf-d4c1d725a7d1 API_KEY
