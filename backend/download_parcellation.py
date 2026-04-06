"""
Download HCP-MMP1.0 parcellation for fsaverage using MNE-Python.
180 regions per hemisphere = 360 total. Gold standard in neuroimaging.
Reference: Glasser et al., 2016, Nature.
"""
import numpy as np
import json
from pathlib import Path
import mne
from mne import read_labels_from_annot

OUTPUT_DIR = Path("./data/regions")
OUTPUT_DIR.mkdir(exist_ok=True)

# MNE sample data includes fsaverage subjects_dir
subjects_dir = mne.datasets.sample.data_path() / "subjects"

print("Downloading HCP-MMP1.0 parcellation...")
mne.datasets.fetch_hcp_mmp_parcellation(
    subjects_dir=subjects_dir,
    verbose=True
)

print("Reading labels...")
labels_lh = read_labels_from_annot(
    "fsaverage", parc="HCPMMP1", hemi="lh",
    subjects_dir=subjects_dir
)
labels_rh = read_labels_from_annot(
    "fsaverage", parc="HCPMMP1", hemi="rh",
    subjects_dir=subjects_dir
)

print(f"Left hemisphere regions : {len(labels_lh)}")
print(f"Right hemisphere regions: {len(labels_rh)}")

# Build vertex → region lookup array (20484 entries)
parcellation = np.zeros(20484, dtype=np.int32)
regions = {}

HCP_NETWORKS = {
    "V1": "Visual", "V2": "Visual", "V3": "Visual", "V4": "Visual",
    "V3A": "Visual", "V3B": "Visual", "V6": "Visual", "V6A": "Visual",
    "V7": "Visual", "V8": "Visual", "PIT": "Visual", "FFC": "Visual",
    "MT": "Visual", "MST": "Visual", "V4t": "Visual", "FST": "Visual",
    "LO1": "Visual", "LO2": "Visual", "LO3": "Visual", "PH": "Visual",
    "A1": "Auditory", "A4": "Auditory", "A5": "Auditory",
    "STSdp": "Auditory", "STSda": "Auditory", "STSvp": "Auditory",
    "STSva": "Auditory", "STGa": "Auditory", "PBelt": "Auditory",
    "MBelt": "Auditory", "LBelt": "Auditory", "RI": "Auditory",
    "TA2": "Language", "44": "Language", "45": "Language",
    "IFSp": "Language", "IFSa": "Language", "IFJp": "Language",
    "IFJa": "Language", "55b": "Language", "STV": "Language",
    "PSL": "Language", "SFL": "Language", "PF": "Language",
    "PFcm": "Language", "PFop": "Language", "PFm": "Language",
    "PFt": "Language", "PGi": "Language", "PGp": "Language",
    "TPOJ1": "Language", "TPOJ2": "Language", "TPOJ3": "Language",
    "POS1": "Default Mode", "POS2": "Default Mode", "RSC": "Default Mode",
    "PCV": "Default Mode", "7m": "Default Mode", "31pv": "Default Mode",
    "31pd": "Default Mode", "31a": "Default Mode", "d23ab": "Default Mode",
    "v23ab": "Default Mode", "DVT": "Default Mode", "ProS": "Default Mode",
    "PHA1": "Default Mode", "PHA2": "Default Mode", "PHA3": "Default Mode",
    "TF": "Default Mode", "TE1a": "Default Mode", "TE1p": "Default Mode",
    "TE1m": "Default Mode", "TE2a": "Default Mode", "TE2p": "Default Mode",
    "TGd": "Default Mode", "TGv": "Default Mode",
    "p9-46v": "Frontoparietal", "a9-46v": "Frontoparietal",
    "46": "Frontoparietal", "9-46d": "Frontoparietal",
    "9a": "Frontoparietal", "9p": "Frontoparietal", "8BL": "Frontoparietal",
    "8Ad": "Frontoparietal", "8Av": "Frontoparietal", "8C": "Frontoparietal",
    "IPS1": "Frontoparietal", "LIPv": "Frontoparietal",
    "LIPd": "Frontoparietal", "VIP": "Frontoparietal", "AIP": "Frontoparietal",
    "MIP": "Frontoparietal", "7PC": "Frontoparietal", "7AL": "Frontoparietal",
    "7Am": "Frontoparietal", "7PL": "Frontoparietal",
    "FEF": "Dorsal Attention", "6r": "Dorsal Attention",
    "6v": "Dorsal Attention", "6a": "Dorsal Attention",
    "PEF": "Dorsal Attention", "IP0": "Dorsal Attention",
    "IP1": "Dorsal Attention", "IP2": "Dorsal Attention",
    "1": "Somatomotor", "2": "Somatomotor", "3a": "Somatomotor",
    "3b": "Somatomotor", "4": "Somatomotor", "6mp": "Somatomotor",
    "6d": "Somatomotor", "SCEF": "Somatomotor", "5L": "Somatomotor",
    "5m": "Somatomotor", "5mv": "Somatomotor", "24dd": "Somatomotor",
    "24dv": "Somatomotor",
    "PoI1": "Salience", "PoI2": "Salience", "PoI3": "Salience",
    "FOP1": "Salience", "FOP2": "Salience", "FOP3": "Salience",
    "FOP4": "Salience", "FOP5": "Salience", "MI": "Salience",
    "AVI": "Salience", "AAIC": "Salience", "Pir": "Salience",
}

HCP_DESCRIPTIONS = {
    "V1": "Primary visual cortex. Processes basic visual features: edges, orientation, contrast and spatial frequency.",
    "V2": "Secondary visual cortex. Integrates simple features from V1, sensitive to illusory contours.",
    "MT": "Middle temporal area. Specialized for visual motion processing and optical flow perception.",
    "A1": "Primary auditory cortex. Encodes frequency, amplitude and basic sound features with tonotopic organization.",
    "STSdp": "Superior temporal sulcus (dorsal posterior). Integrates audiovisual information for speech perception.",
    "44": "Broca's area (pars opercularis). Core region for language production and syntactic processing.",
    "45": "Broca's area (pars triangularis). Involved in semantic processing and language comprehension.",
    "FEF": "Frontal eye fields. Controls voluntary eye movements and spatial attention.",
    "1": "Primary somatosensory cortex (area 1). Processes fine touch and texture discrimination.",
    "3b": "Primary somatosensory cortex (area 3b). Main input zone for tactile information from the body.",
    "4": "Primary motor cortex. Controls voluntary movement execution with somatotopic organization.",
    "PoI2": "Posterior insular cortex area 2. Processes interoceptive signals and autonomic responses.",
}

def get_short_name(label_name, hemi_suffix):
    short = label_name.replace(hemi_suffix, "")
    short = short.replace("L_", "").replace("R_", "").replace("_ROI", "")
    return short

for idx, label in enumerate(labels_lh):
    for v in label.vertices:
        if v < 10242:
            parcellation[v] = idx
    short = get_short_name(label.name, "-lh")
    regions[str(idx)] = {
        "id": idx,
        "name": label.name.replace("-lh", ""),
        "full_name": label.name.replace("-lh", "").replace("_", " "),
        "hemisphere": "L",
        "network": HCP_NETWORKS.get(short, "Association Cortex"),
        "description": HCP_DESCRIPTIONS.get(short,
            f"HCP-MMP1.0 region {short}. Cortical area defined by multimodal neuroimaging (Glasser et al., 2016).")
    }

offset = len(labels_lh)
for idx, label in enumerate(labels_rh):
    for v in label.vertices:
        if v < 10242:
            parcellation[10242 + v] = offset + idx
    short = get_short_name(label.name, "-rh")
    regions[str(offset + idx)] = {
        "id": offset + idx,
        "name": label.name.replace("-rh", ""),
        "full_name": label.name.replace("-rh", "").replace("_", " "),
        "hemisphere": "R",
        "network": HCP_NETWORKS.get(short, "Association Cortex"),
        "description": HCP_DESCRIPTIONS.get(short,
            f"HCP-MMP1.0 region {short}. Cortical area defined by multimodal neuroimaging (Glasser et al., 2016).")
    }

np.save(OUTPUT_DIR / "parcellation.npy", parcellation)
with open(OUTPUT_DIR / "regions.json", "w") as f:
    json.dump(regions, f, indent=2)

print(f"\nSaved parcellation.npy — {len(parcellation)} vertices")
print(f"Saved regions.json     — {len(regions)} regions")
print(f"Unique regions         : {len(np.unique(parcellation))}")
print("Done ✓")