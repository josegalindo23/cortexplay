"""
HCP Multi-Modal Parcellation (HCP-MMP1.0) — Region Metadata

Contains clinical labels and functional descriptions for the 360
cortical regions defined by Glasser et al. (2016, Nature).

Reference:
    Glasser, M.F. et al. (2016). A multi-modal parcellation of
    human cerebral cortex. Nature, 536, 171–178.
"""

# Key regions with clinical descriptions
# Format: region_id -> {name, hemisphere, functional_description, network}
HCP_REGIONS: dict = {
    1: {
        "name": "V1",
        "full_name": "Primary Visual Cortex",
        "hemisphere": "L",
        "description": (
            "Processes basic visual features: edges, orientation, "
            "contrast, and spatial frequency. First cortical stage "
            "of the visual hierarchy."
        ),
        "network": "Visual",
        "brodmann_area": "BA17",
    },
    2: {
        "name": "V2",
        "full_name": "Secondary Visual Cortex",
        "hemisphere": "L",
        "description": (
            "Integrates simple visual features from V1 into more "
            "complex representations. Sensitive to illusory contours."
        ),
        "network": "Visual",
        "brodmann_area": "BA18",
    },
    3: {
        "name": "V3",
        "full_name": "Visual Area V3",
        "hemisphere": "L",
        "description": (
            "Processes motion and depth information. Projects to "
            "both dorsal and ventral visual streams."
        ),
        "network": "Visual",
        "brodmann_area": "BA19",
    },
    4: {
        "name": "A1",
        "full_name": "Primary Auditory Cortex",
        "hemisphere": "L",
        "description": (
            "First cortical stage of auditory processing. Encodes "
            "frequency (tonotopy), amplitude, and basic sound features."
        ),
        "network": "Auditory",
        "brodmann_area": "BA41",
    },
    5: {
        "name": "STSdp",
        "full_name": "Superior Temporal Sulcus (dorsal posterior)",
        "hemisphere": "L",
        "description": (
            "Integrates audiovisual information. Critical for speech "
            "perception and biological motion understanding."
        ),
        "network": "Language",
        "brodmann_area": "BA22",
    },
    # ... remaining 355 regions follow same structure
    # Full dataset loaded from regions/hcp_regions.json at runtime
}

# Functional networks in HCP parcellation
HCP_NETWORKS: list = [
    "Visual",
    "Auditory",
    "Language",
    "Default Mode",
    "Frontoparietal",
    "Dorsal Attention",
    "Ventral Attention",
    "Somatomotor",
    "Limbic",
]

# TRIBE v2 modalities
MODALITIES: list = ["video", "audio", "text", "multimodal"]

# fMRI temporal resolution (TR) used in TRIBE v2
TR_SECONDS: float = 1.0  # 1 second per timepoint