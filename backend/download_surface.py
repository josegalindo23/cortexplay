# backend/download_surface.py
"""Download fsaverage5 brain surface geometry from nilearn."""
import numpy as np
import json
from nilearn import datasets
import os

from nilearn import surface

OUTPUT_DIR = "D:/Documents/DEV/cortexplay/backend/data/surface"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Downloading fsaverage5 surface...")
fsaverage = datasets.fetch_surf_fsaverage(mesh='fsaverage5')

print("Processing left hemisphere...")

coords_l, faces_l = surface.load_surf_mesh(fsaverage.pial_left)
coords_r, faces_r = surface.load_surf_mesh(fsaverage.pial_right)

print(f"Left hemisphere  : {coords_l.shape[0]} vertices, {faces_l.shape[0]} faces")
print(f"Right hemisphere : {coords_r.shape[0]} vertices, {faces_r.shape[0]} faces")
print(f"Total vertices   : {coords_l.shape[0] + coords_r.shape[0]}")

# Save as numpy
np.save(f"{OUTPUT_DIR}/coords_left.npy", coords_l)
np.save(f"{OUTPUT_DIR}/coords_right.npy", coords_r)
np.save(f"{OUTPUT_DIR}/faces_left.npy", faces_l)
np.save(f"{OUTPUT_DIR}/faces_right.npy", faces_r)

# Save as JSON for frontend
surface_data = {
    "left": {
        "vertices": coords_l.tolist(),
        "faces": faces_l.tolist(),
        "n_vertices": int(coords_l.shape[0])
    },
    "right": {
        "vertices": coords_r.tolist(),
        "faces": faces_r.tolist(),
        "n_vertices": int(coords_r.shape[0])
    },
    "total_vertices": int(coords_l.shape[0] + coords_r.shape[0])
}

with open(f"{OUTPUT_DIR}/fsaverage5.json", "w") as f:
    json.dump(surface_data, f)

print(f"\nSaved to {OUTPUT_DIR}")
print("Surface geometry ready ✓")