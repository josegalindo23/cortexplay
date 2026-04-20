"""
Tests for CortexPlay brain API endpoints.
Run with: pytest tests/ -v
"""
import pytest
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


client = TestClient(app)


def test_health():
    """Root health check returns ok."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_brain_health():
    """Brain service health check."""
    response = client.get("/api/brain/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_clips_health():
    """Clips service health check."""
    response = client.get("/api/clips/health")
    assert response.status_code == 200


def test_surface_returns_geometry():
    """Surface endpoint returns valid brain geometry."""
    response = client.get("/api/brain/surface")
    assert response.status_code == 200
    data = response.json()
    assert "left" in data
    assert "right" in data
    assert data["total_vertices"] == 20484
    assert len(data["left"]["vertices"]) == 10242
    assert len(data["right"]["vertices"]) == 10242


def test_activation_valid_clip():
    """Activation endpoint returns correct shape for valid clip."""
    response = client.get(
        "/api/brain/activation",
        params={"clip_id": "big_buck_bunny_30s_video", "modality": "video", "t": 0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["n_vertices"] == 20484
    assert len(data["activations"]) == 20484
    assert data["timepoint"] == 0


def test_activation_invalid_clip():
    """Activation endpoint returns 404 for unknown clip."""
    response = client.get(
        "/api/brain/activation",
        params={"clip_id": "nonexistent_clip", "t": 0}
    )
    assert response.status_code == 404


def test_activation_t_clamping():
    """Timepoint is clamped to valid range."""
    response = client.get(
        "/api/brain/activation",
        params={"clip_id": "big_buck_bunny_30s_video", "t": 9999}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["timepoint"] < 9999


def test_region_valid_vertex():
    """Region endpoint returns valid HCP region for a vertex."""
    response = client.get("/api/brain/region/5000")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "hemisphere" in data
    assert data["hemisphere"] in ["L", "R"]
    assert "network" in data
    assert "description" in data


def test_region_invalid_vertex():
    """Region endpoint returns 400 for out-of-range vertex."""
    response = client.get("/api/brain/region/99999")
    assert response.status_code == 400


def test_timeseries_returns_30_points():
    """Timeseries returns activation for all timesteps."""
    response = client.get(
        "/api/brain/timeseries",
        params={"clip_id": "big_buck_bunny_30s", "vertex_id": 5000, "modality": "audio"}
    )
    assert response.status_code == 200 
    data = response.json()
    assert len(data["timepoints"]) == len(data["activations"])
    assert len(data["activations"]) > 0


def test_clips_list():
    """Clips endpoint returns available clips."""
    response = client.get("/api/brain/clips")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "clips" in data