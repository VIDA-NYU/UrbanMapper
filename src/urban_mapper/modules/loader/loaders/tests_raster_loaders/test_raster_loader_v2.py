"""
Test suite for the RasterLoader class.

This module contains unit tests for verifying the functionality of the RasterLoader class,
which is responsible for loading and processing raster data files.

Tests cover:
    - Basic initialization of RasterLoader
    - Setter methods for loading parameters
    - Error handling for missing files and invalid data
    - GeoTIFF file loading functionality
    - PNG with world file loading functionality
    - Preview functionality testing

Requirements:
    - pytest
    - urban_mapper package
    - Test data files:
        * ./data/output_be.tif
        * ./data/lower_manhattan_dem.png
        * ./data/lower_manhattan_dem.pngw

How to run:
    From the project root directory:
    $ pytest test_raster_loader_v2.py -v

    To run a specific test:
    $ pytest test_raster_loader_v2.py::test_geotiff_loading -v

    To run with detailed output:
    $ pytest test_raster_loader_v2.py -v --capture=no
"""

import pytest
from urban_mapper.modules.loader.loaders.raster_loader import RasterLoader
from PIL import Image
import numpy as np
import os

def test_raster_loader_initialization():
    """Test the basic initialization of RasterLoader with a dummy file path"""
    loader = RasterLoader("fake_path.tif")
    assert str(loader.file_path) == "fake_path.tif"

def test_raster_loader_setters():
    """Test all setter methods of RasterLoader to ensure they properly update instance variables"""
    loader = RasterLoader("fake_path.tif")
    loader.set_raster_strategy("points")
    loader.set_sampling_factor(0.5)
    loader.set_band_selection([1,2,3])
    loader.set_nodata_handling("ignore")
    loader.set_max_pixels(10000)
    assert loader.raster_strategy == "points"
    assert loader.sampling_factor == 0.5
    assert loader.band_selection == [1,2,3]
    assert loader.nodata_handling == "ignore"
    assert loader.max_pixels == 10000


def test_raster_loader_load_missing_file():
    """Test error handling when attempting to load a non-existent file"""
    loader = RasterLoader("fake_path.tif")
    with pytest.raises(RuntimeError) as excinfo:
        loader._load_data_from_file()
    assert "No such file or directory" in str(excinfo.value)


def test_geotiff_loading():
    """Test successful loading of a GeoTIFF file and verify the returned data structure"""
    test_path = os.path.join(os.path.dirname(__file__), "..", "data", "output_be.tif")
    if not os.path.exists(test_path):
        pytest.skip("GeoTIFF for test missing")
    loader = RasterLoader(test_path)
    result = loader._load_data_from_file()
    assert "data_shape" in result
    assert "data_dtype" in result
    assert "crs" in result
    assert "transform" in result


def test_load_png_with_worldfile_success():
    """Test successful loading of a PNG file with its associated world file"""
    test_png_path = os.path.join(os.path.dirname(__file__), "..","data", "lower_manhattan_dem.png")
    if not os.path.exists(test_png_path):
        pytest.skip("Test PNG file is missing")
    
    loader = RasterLoader(test_png_path)
    result = loader._load_png_with_worldfile()
    
    # Verify the result structure
    assert isinstance(result, dict)
    assert "data_shape" in result
    assert "data_dtype" in result
    assert "transform" in result
    assert "crs" in result
    
    # Verify world file parameters
    assert len(result["transform"]) == 6

def test_load_png_without_worldfile():
    """Test error handling when attempting to load a PNG file without an associated world file"""
    # Create a temporary PNG file without a world file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        # Créer une petite image test
        img_array = np.zeros((10, 10), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(tmp.name)
        tmp_path = tmp.name
    
    loader = RasterLoader(tmp_path)
    with pytest.raises(FileNotFoundError) as excinfo:
        loader._load_png_with_worldfile()
    assert "No world file found" in str(excinfo.value)
    
    # Cleanup
    os.remove(tmp_path)

def test_load_png_with_invalid_worldfile():
    """Test error handling when attempting to load a PNG file with an invalid world file format"""
    # Create temporary test files
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
        # Créer une petite image test
        img_array = np.zeros((10, 10), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(tmp_png.name)
        png_path = tmp_png.name
    with open(png_path + "w", "w") as tmp_world:
        tmp_world.write("invalid\ndata")  # Fichier world invalide
    
    loader = RasterLoader(png_path)
    with pytest.raises(ValueError) as excinfo:
        loader._load_png_with_worldfile()
    assert "could not convert string to" in str(excinfo.value)
    
    # Cleanup
    os.remove(png_path)
    os.remove(png_path + "w")

def test_preview_not_implemented():
    """Test that the preview method correctly raises NotImplementedError"""
    loader = RasterLoader("fake_path.tif")
    with pytest.raises(NotImplementedError) as excinfo:
        loader.preview()
    assert "Raster preview is not yet implemented" in str(excinfo.value)

