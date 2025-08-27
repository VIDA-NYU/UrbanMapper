"""
Unit tests for the RasterLoader class.

This module contains unit tests that verify the functionality of the RasterLoader class,
which is responsible for loading and handling raster data files.

Test Coverage:
-------------
- Initialization of RasterLoader
- Loading valid raster files
- Error handling for invalid file paths
- Metadata extraction and validation

Requirements:
------------
- pytest
- numpy
- rasterio
- urban_mapper package

How to Run:
----------
From the project root directory:
    pytest src/urban_mapper/modules/loader/loaders/tests/test_raster_loader.py -v

Or to run with coverage report:
    pytest --cov=urban_mapper.modules.loader.loaders.raster_loader src/urban_mapper/modules/loader/loaders/tests/test_raster_loader.py
"""

import pytest
import numpy as np
import os
from pathlib import Path
from urban_mapper.modules.loader.loaders.raster_loader import RasterLoader

def test_raster_loader_initialization():
    """
    Test RasterLoader initialization.
    
    Verifies that:
    - The loader can be instantiated
    - The file path is correctly stored
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'output_be.tif')
    loader = RasterLoader(file_path)
    assert loader is not None
    assert Path(loader.file_path) == Path(file_path)

def test_load_valid_raster():
    """
    Test loading of a valid raster file.
    
    Verifies that:
    - The loader can read the raster file
    - The returned data is a numpy array
    - The data is not empty
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'output_be.tif')
    loader = RasterLoader(file_path)
    data = loader._load_data_from_file()  
    assert data is not None
    assert isinstance(data, np.ndarray)

def test_invalid_file_path():
    """
    Test error handling for invalid file paths.
    
    Verifies that:
    - The loader raises a RuntimeError when trying to load a non-existent file
    - Error handling works as expected
    """
    loader = RasterLoader("invalid/path/to/file.tif")
    with pytest.raises(RuntimeError):  
        loader._load_data_from_file()

def test_raster_metadata():
    """
    Test metadata extraction from raster file.
    
    Verifies that:
    - Metadata can be extracted
    - Required metadata fields are present (width, height, count)
    - Metadata values are accessible
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'output_be.tif')
    loader = RasterLoader(file_path)
    loader._load_data_from_file()  # Load data to get metadata
    assert loader.meta is not None
    assert 'width' in loader.meta
    assert 'height' in loader.meta
    assert 'count' in loader.meta


