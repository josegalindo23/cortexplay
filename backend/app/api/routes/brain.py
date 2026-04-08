"""
Brain activation and surface geometry endpoints.

Serves fsaverage5 surface mesh and TRIBE v2 fMRI predictions
for the CortexPlay interactive visualizer.
"""

import json
import numpy as np
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from functools import lru_cache


router = APIRouter()

SURFACE_PATH     = Path("./data/surface/fsaverage5.json")
PREDICTIONS_DIR  = Path("./data/predictions")
PARCELLATION_PATH = Path("./data/regions/parcellation.npy")
REGIONS_PATH      = Path("./data/regions/regions.json")


@router.get("/health")
async def brain_health():
    """Verify brain service is operational."""
    return {"status": "ok", "service": "brain"}


@router.get("/surface")
async def get_surface():
    """
    Return fsaverage5 cortical surface geometry.

    Returns vertex coordinates and face indices for both
    hemispheres of the fsaverage5 surface mesh (20,484 vertices).
    """
    if not SURFACE_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Surface geometry not found. Run download_surface.py first."
        )
    with open(SURFACE_PATH, "r") as f:
        return json.load(f)


@router.get("/activation")
async def get_activation(
    clip_id:  str = Query(...),
    modality: str = Query("video"),
    t:        int = Query(0, ge=0),
):
    
    """
    Return brain activation values for a specific timepoint.
    Uses real TRIBE v2 predictions per modality.
    """

    pred_path = PREDICTIONS_DIR / f"{clip_id}_{modality}.npy"
    if not pred_path.exists():
        pred_path = PREDICTIONS_DIR / f"{clip_id}.npy"  # fallback to raw predictions
    if not pred_path.exists():
        raise HTTPException(status_code=404, detail=f"Predictions not found for clip '{clip_id}'")

    preds = np.load(str(pred_path))
    t = min(t, preds.shape[0] - 1)

    return {
        "clip_id":     clip_id,
        "modality":    modality,
        "timepoint":   t,
        "n_timesteps": preds.shape[0],
        "n_vertices":  preds.shape[1],
        "activations": preds[t].tolist(),
    }


@router.get("/clips")
async def get_clips():
    """
    Return list of available pre-processed clips.

    Scans the predictions directory for available .npy files
    and returns their metadata.
    """
    clips = []
    for meta_path in PREDICTIONS_DIR.glob("*_meta.json"):
        with open(meta_path, "r") as f:
            clips.append(json.load(f))

    return {
        "total": len(clips),
        "clips": clips
    }

@lru_cache(maxsize=1)
def load_parcellation():
    """Load parcellation and regions once, cache in memory."""
    parcellation = np.load(str(PARCELLATION_PATH))
    with open(REGIONS_PATH, "r") as f:
        regions = json.load(f)
    return parcellation, regions

@router.get("/region/{vertex_id}")
async def get_region_info(vertex_id: int):
    """
    Return clinical info for the brain region containing a vertex.
    Uses HCP-MMP1.0 parcellation (Glasser et al., 2016, Nature).
    180 regions per hemisphere, gold standard in neuroimaging.
    """
    if vertex_id < 0 or vertex_id >= 20484:
        raise HTTPException(status_code=400, detail="vertex_id must be 0-20483")

    parcellation, regions = load_parcellation()
    region_id = int(parcellation[vertex_id])
    region = regions.get(str(region_id))

    if not region:
        raise HTTPException(status_code=404, detail=f"Region not found for vertex {vertex_id}")

    return {
        "vertex_id":  vertex_id,
        "region_id":  region_id,
        "name":       region["name"],
        "full_name":  region["full_name"],
        "hemisphere": region["hemisphere"],
        "network":    region["network"],
        "description": region["description"],
    }

@router.get("/timeseries")
async def get_timeseries(
    clip_id: str = Query(...),
    modality: str = Query("video"),
    vertex_id: int = Query(...),
):
    """Return activation time series for a specific vertex."""
    pred_path = PREDICTIONS_DIR / f"{clip_id}_{modality}.npy"
    if not pred_path.exists():
        raise HTTPException(status_code=404, detail="Predictions not found")

    preds = np.load(str(pred_path))
    series = preds[:, vertex_id].tolist()

    return {
        "vertex_id": vertex_id,
        "clip_id": clip_id,
        "timepoints": list(range(len(series))),
        "activations": series,
    }