"""
Pydantic schemas for brain activation API responses.

These models define the contract between the backend and frontend,
ensuring type safety and automatic validation on all endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class VertexActivation(BaseModel):
    """Activation value for a single cortical vertex."""

    vertex_id: int = Field(..., description="Vertex index in fsaverage5 mesh (0-20483)")
    activation: float = Field(..., ge=0.0, le=1.0, description="Normalized activation value")


class BrainActivationResponse(BaseModel):
    """
    Full brain activation map for a given clip, modality, and timepoint.

    Returns activation values for all 20,484 vertices of the
    fsaverage5 cortical surface mesh.
    """

    clip_id: str = Field(..., description="Video clip identifier")
    modality: str = Field(..., description="Modality: video | audio | text | multimodal")
    timepoint: float = Field(..., description="Time in seconds within the clip")
    activations: List[float] = Field(
        ...,
        description="Activation values for all 20,484 vertices, normalized to [0, 1]",
        min_length=20484,
        max_length=20484,
    )
    n_vertices: int = Field(20484, description="Total number of cortical vertices")


class RegionInfo(BaseModel):
    """Clinical metadata for a single HCP brain region."""

    region_id: int = Field(..., description="HCP region index (1-360)")
    name: str = Field(..., description="Short region name (e.g., 'V1')")
    full_name: str = Field(..., description="Full clinical name")
    hemisphere: str = Field(..., description="Hemisphere: L or R")
    description: str = Field(..., description="Clinical functional description")
    network: str = Field(..., description="Functional network membership")
    brodmann_area: Optional[str] = Field(None, description="Corresponding Brodmann area")
    activation: Optional[float] = Field(None, description="Current activation value if available")


class RegionsResponse(BaseModel):
    """List of all HCP parcellation regions with metadata."""

    total: int = Field(..., description="Total number of regions")
    regions: List[RegionInfo]


class ClipInfo(BaseModel):
    """Metadata for a video clip available for analysis."""

    clip_id: str = Field(..., description="Unique clip identifier")
    title: str = Field(..., description="Human-readable clip title")
    duration_seconds: float = Field(..., description="Clip duration in seconds")
    modalities_available: List[str] = Field(..., description="Available modalities for this clip")
    thumbnail_url: Optional[str] = Field(None, description="URL to clip thumbnail")
    description: Optional[str] = Field(None, description="Brief clip description")


class ClipsResponse(BaseModel):
    """List of available video clips."""

    total: int
    clips: List[ClipInfo]


class TimeSeriesResponse(BaseModel):
    """
    Activation time series for a specific brain region.

    Used to populate the Recharts time series graph in the frontend.
    """

    region_id: int
    region_name: str
    clip_id: str
    modality: str
    timepoints: List[float] = Field(..., description="Time values in seconds")
    activations: List[float] = Field(..., description="Activation values per timepoint")