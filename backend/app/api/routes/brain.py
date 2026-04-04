"""
Brain activation and surface geometry endpoints.

Serves fsaverage5 surface mesh and TRIBE v2 fMRI predictions
for the CortexPlay interactive visualizer.
"""

import json
import numpy as np
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter()

SURFACE_PATH     = Path("./data/surface/fsaverage5.json")
PREDICTIONS_DIR  = Path("./data/predictions")


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
    clip_id:  str = Query(..., description="Clip identifier"),
    modality: str = Query("video", description="video | audio | text | multimodal"),
    t:        int = Query(0, description="Timepoint in seconds", ge=0),
):
    """
    Return brain activation values for a specific timepoint.

    Loads pre-computed TRIBE v2 predictions and returns the
    activation array for all 20,484 cortical vertices at time t.

    Args:
        clip_id:  Identifier of the video clip
        modality: Stimulus modality (video, audio, text, multimodal)
        t:        Timepoint in seconds (0-indexed)

    Returns:
        JSON with activations array of length 20,484
    """
    pred_path = PREDICTIONS_DIR / f"{clip_id}.npy"

    if not pred_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Predictions not found for clip '{clip_id}'. Run save_predictions.py first."
        )

    preds = np.load(str(pred_path))
    n_timesteps = preds.shape[0]

    # Clamp t to valid range
    t = min(t, n_timesteps - 1)

    activations = preds[t].tolist()

    return {
        "clip_id":     clip_id,
        "modality":    modality,
        "timepoint":   t,
        "n_timesteps": n_timesteps,
        "n_vertices":  len(activations),
        "activations": activations,
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