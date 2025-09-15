#!/bin/bash
# start.sh

# Activate the conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate spatial-bias-env

# Start the FastAPI server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
