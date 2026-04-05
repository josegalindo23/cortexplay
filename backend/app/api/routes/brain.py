"""
Brain activation and surface geometry endpoints.

Serves fsaverage5 surface mesh and TRIBE v2 fMRI predictions
for the CortexPlay interactive visualizer.
"""

import json
import numpy as np
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

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
    clip_id:  str = Query(...),
    modality: str = Query("video"),
    t:        int = Query(0, ge=0),
):
    pred_path = PREDICTIONS_DIR / f"{clip_id}.npy"
    if not pred_path.exists():
        raise HTTPException(status_code=404, detail=f"Predictions not found for clip '{clip_id}'")

    preds = np.load(str(pred_path))
    t = min(t, preds.shape[0] - 1)
    activations = preds[t].copy()

    # Modality simulation based on cortical region weights
    # Visual cortex: vertices 0-2000 (occipital)
    # Auditory cortex: vertices 4500-6000 (temporal)
    # Language network: vertices 6000-8000 (frontal-temporal)
    if modality == "audio":
        activations *= 0.3
        activations[4500:6000] *= 4.0
        activations[10242+4500:10242+6000] *= 4.0
    elif modality == "text":
        activations *= 0.2
        activations[6000:8000] *= 5.0
        activations[10242+6000:10242+8000] *= 5.0
    elif modality == "multimodal":
        pass  # use raw predictions — all modalities combined

    return {
        "clip_id":     clip_id,
        "modality":    modality,
        "timepoint":   t,
        "n_timesteps": preds.shape[0],
        "n_vertices":  len(activations),
        "activations": activations.tolist(),
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

@router.get("/region/{vertex_id}")
async def get_region_info(vertex_id: int):
    """
    Return clinical info for the brain region containing a vertex.
    Uses a simplified mapping based on vertex index ranges.
    """
    # Simplified HCP region mapping by vertex position
    # Left hemisphere: 0-10241, Right: 10242-20483
    hemisphere = "L" if vertex_id < 10242 else "R"
    local_id = vertex_id if vertex_id < 10242 else vertex_id - 10242

    # Approximate region based on vertex position
    region_pct = local_id / 10242

    if region_pct < 0.15:
        region = {"name": "V1", "full_name": "Primary Visual Cortex",
                  "description": "Processes basic visual features: edges, orientation, contrast and spatial frequency. First cortical stage of the visual hierarchy.",
                  "network": "Visual", "brodmann": "BA17"}
    elif region_pct < 0.25:
        region = {"name": "V2", "full_name": "Secondary Visual Cortex",
                  "description": "Integrates simple visual features from V1. Sensitive to illusory contours and figure-ground segregation.",
                  "network": "Visual", "brodmann": "BA18"}
    elif region_pct < 0.35:
        region = {"name": "MT+", "full_name": "Middle Temporal Complex",
                  "description": "Specialized for visual motion processing. Critical for perceiving moving objects and optical flow.",
                  "network": "Visual", "brodmann": "BA19"}
    elif region_pct < 0.45:
        region = {"name": "A1", "full_name": "Primary Auditory Cortex",
                  "description": "First cortical stage of auditory processing. Encodes frequency, amplitude and basic sound features.",
                  "network": "Auditory", "brodmann": "BA41"}
    elif region_pct < 0.55:
        region = {"name": "STS", "full_name": "Superior Temporal Sulcus",
                  "description": "Integrates audiovisual information. Critical for speech perception and biological motion.",
                  "network": "Language", "brodmann": "BA22"}
    elif region_pct < 0.65:
        region = {"name": "IFG", "full_name": "Inferior Frontal Gyrus",
                  "description": "Broca's area. Core region for language production and syntactic processing.",
                  "network": "Language", "brodmann": "BA44"}
    elif region_pct < 0.75:
        region = {"name": "mPFC", "full_name": "Medial Prefrontal Cortex",
                  "description": "Involved in social cognition, self-referential processing and narrative comprehension.",
                  "network": "Default Mode", "brodmann": "BA10"}
    elif region_pct < 0.85:
        region = {"name": "PPC", "full_name": "Posterior Parietal Cortex",
                  "description": "Integrates sensory information for spatial awareness and attention direction.",
                  "network": "Dorsal Attention", "brodmann": "BA7"}
    else:
        region = {"name": "SMC", "full_name": "Sensorimotor Cortex",
                  "description": "Processes touch, proprioception and motor planning.",
                  "network": "Somatomotor", "brodmann": "BA1"}

    return {
        "vertex_id": vertex_id,
        "hemisphere": hemisphere,
        **region
    }

@router.get("/timeseries")
async def get_timeseries(
    clip_id: str = Query(...),
    vertex_id: int = Query(...),
):
    """Return activation time series for a specific vertex."""
    pred_path = PREDICTIONS_DIR / f"{clip_id}.npy"
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