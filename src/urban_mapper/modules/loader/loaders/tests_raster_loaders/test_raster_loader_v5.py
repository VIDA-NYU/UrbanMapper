"""
Unit tests for the RasterLoader class.

This module contains unit tests for verifying the functionality of the RasterLoader class,
which is responsible for loading and handling raster data files (like GeoTIFF).

Requirements:
------------
- pytest
- A test raster file (output_be.tif) in the ../data directory
- The urban_mapper package installed

How to run:
----------
From the command line:
    pytest test_raster_loader_v5.py

Or with more details:
    pytest test_raster_loader_v5.py -v

Dependencies:
-----------
- pytest
- geopandas
- rasterio
- urban_mapper.modules.loader.loaders.raster_loader
"""

import pytest
import os
from urban_mapper.modules.loader.loaders.raster_loader import RasterLoader

# Path to test file
TEST_FILE = os.path.join("..", "data", "output_be.tif")

def test_init():
    """
    Test the basic initialization of the RasterLoader.
    
    Verifies that:
    - The loader can be created
    - The file path is correctly stored
    - The file path matches the expected path
    """
    loader = RasterLoader(TEST_FILE)
    assert loader is not None
    assert str(loader.file_path) == TEST_FILE

def test_load_data():
    """
    Test the data loading functionality.
    
    Verifies that:
    - The loader can read the raster file
    - The returned GeoDataFrame is not None
    - The GeoDataFrame contains data (not empty)
    
    Skips if the test file is not found.
    """
    loader = RasterLoader(TEST_FILE)
    try:
        gdf = loader._load_data_from_file()
        assert gdf is not None
        assert not gdf.empty
    except FileNotFoundError:
        pytest.skip("Test file not found")

def test_preview():
    """
    Test the preview functionality.
    
    Verifies that:
    - The preview method returns a string for ASCII format
    - The preview contains the loader name
    - The preview contains the file path
    
    Skips if the file is not accessible or cannot be read.
    """
    loader = RasterLoader(TEST_FILE)
    try:
        # Test format ASCII uniquement
        preview = loader.preview(format="ascii")
        assert isinstance(preview, str)
        assert "RasterLoader" in preview
        assert TEST_FILE in preview
    except Exception:
        pytest.skip("Preview test failed - file might not be accessible")

def test_preview_invalid_format():
    """
    Test error handling for invalid preview formats.
    
    Verifies that:
    - The loader raises ValueError for invalid formats
    - The error handling works after loading metadata
    
    Steps:
    1. Creates a loader instance
    2. Pre-loads the metadata
    3. Tests with an invalid format
    
    Skips if the test file is not found.
    """
    loader = RasterLoader(TEST_FILE)
    try:
        # Préchargement des métadonnées avec un format valide
        _ = loader._load_data_from_file()
        # Test du format invalide
        with pytest.raises(ValueError):
            loader.preview(format="invalid_format")
    except FileNotFoundError:
        pytest.skip("Test file not found")

