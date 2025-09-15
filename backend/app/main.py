# src/api/main.py

from dotenv import load_dotenv
import os

load_dotenv()

print("Gurobi Access ID:", os.getenv("GRB_WLSACCESSID"))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.spatial_bias.router import router as spatial_bias_router

app = FastAPI(title="Spatial Bias Audit & Mitigation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(
    spatial_bias_router, prefix="/api/spatial-bias", tags=["Spatial Bias"]
)
