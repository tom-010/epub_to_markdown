#!/bin/bash

python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python -m spacy download en_core_web_sm