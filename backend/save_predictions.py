"""
Save TRIBE v2 predictions to disk for use in CortexPlay API.
Run ONCE per clip — results cached for instant API serving.
Optimized: frequency=0.5 reduces processing time by 4x.
"""
import os
import json
import numpy as np

os.environ["HF_HUB_OFFLINE"] = "1"

from tribev2 import TribeModel

VIDEO_PATH = "D:/Documents/DEV/cortexplay/backend/test_video_30s.mp4"
CACHE_DIR  = "D:/cx_cache"
OUTPUT_DIR = "D:/Documents/DEV/cortexplay/backend/data/predictions"
CLIP_ID    = "big_buck_bunny_30s"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading model...")
model = TribeModel.from_pretrained(
    "facebook/tribev2",
    cache_folder=CACHE_DIR,
    config_update={
        "data.num_workers": 0,
        "data.batch_size": 1,
        "data.video_feature.frequency": 2.0,
        "data.audio_feature.frequency": 2.0,
        "data.video_feature.n_layers_to_use": 8,
        "data.audio_feature.n_layers_to_use": 8,
    }
)
print(f"Video frequency: {model.data.video_feature.frequency}")

print("Processing video...")
df = model.get_events_dataframe(video_path=VIDEO_PATH)
preds, segments = model.predict(events=df)

print(f"Shape: {preds.shape}")

# Save numpy array
np.save(f"{OUTPUT_DIR}/{CLIP_ID}.npy", preds)

# Save metadata
metadata = {
    "clip_id": CLIP_ID,
    "title": "Big Buck Bunny (30s)",
    "duration_seconds": float(preds.shape[0]),
    "n_timesteps": int(preds.shape[0]),
    "n_vertices": int(preds.shape[1]),
    "value_range": [float(preds.min()), float(preds.max())],
    "mean_activation": float(preds.mean()),
    "modality": "video",
    "frequency_hz": 0.5,
    "model": "TRIBE v2",
    "citation": "d'Ascoli et al., 2026, Meta FAIR",
}

with open(f"{OUTPUT_DIR}/{CLIP_ID}_meta.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"\nSaved: {CLIP_ID}.npy")
print(f"Saved: {CLIP_ID}_meta.json")
print("Done ✓")