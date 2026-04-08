"""
Save TRIBE v2 predictions to disk for use in CortexPlay API.
Usage:
  python save_predictions.py --modality video
  python save_predictions.py --modality audio
  python save_predictions.py --modality text
"""
import os
import json
import numpy as np
import argparse
from tribev2 import TribeModel

os.environ["HF_HUB_OFFLINE"] = "1"

parser = argparse.ArgumentParser()
parser.add_argument("--modality", default = "video", choices=["video", "audio", "text"])
args = parser.parse_args()

CACHE_DIR  = "D:/cx_cache"
OUTPUT_DIR = "D:/Documents/DEV/cortexplay/backend/data/predictions"
CLIP_ID    = "big_buck_bunny_30s"
os.makedirs(OUTPUT_DIR, exist_ok=True)

INPUT_MAP = {
    "video": {"video_path": "D:/Documents/DEV/cortexplay/backend/test_video_30s.mp4"},
    "audio": {"audio_path": "D:/Documents/DEV/cortexplay/backend/data/videos/big_buck_bunny_30s_audio.wav"},
    "text":  {"text_path":  "D:/Documents/DEV/cortexplay/backend/data/videos/big_buck_bunny_30s_text.txt"},
}

print(f"Loading TRIBE v2 — modality: {args.modality}")

if args.modality == "text":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    config_update = {
        "data.num_workers": 0,
        "data.batch_size": 1,
        "data.video_feature.frequency": 2.0,
        "data.audio_feature.frequency": 2.0,
        "data.text_feature.device": "cpu",
    }
else:
    config_update = {
        "data.num_workers": 0,
        "data.batch_size": 1,
        "data.video_feature.frequency": 2.0,
        "data.audio_feature.frequency": 2.0,
    }

model = TribeModel.from_pretrained(
    "facebook/tribev2",
    cache_folder=CACHE_DIR,
    config_update= config_update,
    # {
    #     "data.num_workers": 0,
    #     "data.batch_size": 1,
    #     "data.video_feature.frequency": 2.0,
    #     "data.audio_feature.frequency": 2.0,
    #     # "data.video_feature.n_layers_to_use": 8,
    #     # "data.audio_feature.n_layers_to_use": 8,
    # }
)

print("Processing input...")
df = model.get_events_dataframe(**INPUT_MAP[args.modality])
preds, _ = model.predict(events=df)

print(f"Shape: {preds.shape}")

# Save
np.save(f"{OUTPUT_DIR}/{CLIP_ID}_{args.modality}.npy", preds)

metadata = {
    "clip_id": f"{CLIP_ID}_{args.modality}",
    "title": f"Big Buck Bunny 30s ({args.modality})",
    "duration_seconds": float(preds.shape[0]),
    "n_timesteps": int(preds.shape[0]),
    "n_vertices": int(preds.shape[1]),
    "value_range": [float(preds.min()), float(preds.max())],
    "mean_activation": float(preds.mean()),
    "modality": args.modality,
    "model": "TRIBE v2",
    "citation": "d'Ascoli et al., 2026, Meta FAIR",
}
with open(f"{OUTPUT_DIR}/{CLIP_ID}_{args.modality}_meta.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"Saved: {CLIP_ID}_{args.modality}.npy ✓")