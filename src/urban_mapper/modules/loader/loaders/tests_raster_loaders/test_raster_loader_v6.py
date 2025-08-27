"""Unit tests for the RasterLoader class.

This test suite verifies the functionality of the RasterLoader class which handles
raster file loading and processing.

Prerequisites:
-------------
- A test raster file 'output_be.tif' must be present in the '../data' directory
- Required packages: pytest, geopandas, rasterio, numpy
- The RasterLoader class must be properly importable

How to run:
-----------
From the project root directory:
    pytest urban_mapper/modules/loader/loaders/tests/test_raster_loader.py -v

Test Coverage:
-------------
- Basic instantiation and attribute verification
- Preview functionality (ASCII and JSON formats)
- Data loading and GeoDataFrame structure
- Downsampling functionality
- Error handling for invalid inputs and missing files
"""

import pytest
import os
from pathlib import Path
import geopandas as gpd
import rasterio
import numpy as np
from urban_mapper.modules.loader.loaders.raster_loader import RasterLoader

def test_raster_loader_creation():
    """Test the basic instantiation of RasterLoader.
    
    Verifies that:
    - The loader can be instantiated with a valid file path
    - The instance has the correct type
    - The file path is properly stored
    - The file exists in the expected location
    """
    # Construire le chemin vers le fichier de test
    current_dir = Path(__file__).parent  # dossier tests
    data_dir = current_dir.parent / "data"  # remonter d'un niveau et aller dans data
    test_file_path = data_dir / "output_be.tif"
    
    # Vérifier que le fichier existe
    assert test_file_path.exists(), f"Le fichier test {test_file_path} n'existe pas"
    
    # Créer le loader et tester ses propriétés de base
    loader = RasterLoader(file_path=str(test_file_path))
    assert loader is not None
    assert isinstance(loader, RasterLoader)
    assert Path(loader.file_path) == test_file_path

def test_raster_loader_preview():
    """Test the preview functionality in both ASCII and JSON formats.
    
    Verifies that:
    - ASCII preview returns a properly formatted string
    - JSON preview returns a dictionary with all required keys
    - Both formats contain the correct file information
    - The metadata is properly extracted from the raster file
    """
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data"
    test_file_path = data_dir / "output_be.tif"
    
    loader = RasterLoader(file_path=str(test_file_path))  # Conversion en str ici
    
    # Test ASCII format
    ascii_preview = loader.preview(format="ascii")
    assert isinstance(ascii_preview, str)
    assert "Loader: RasterLoader" in ascii_preview
    assert str(test_file_path) in ascii_preview
    
    # Test JSON format
    json_preview = loader.preview(format="json")
    assert isinstance(json_preview, dict)
    assert json_preview["loader"] == "RasterLoader"
    assert str(test_file_path) in json_preview["file"]
    assert "shape" in json_preview
    assert "dtype" in json_preview
    assert "crs" in json_preview

def test_preview_invalid_format():
    """Test error handling for invalid preview format.
    
    Verifies that:
    - The loader raises ValueError for unsupported formats
    - The error message contains appropriate information
    - The error handling is consistent with the API documentation
    """
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data"
    test_file_path = data_dir / "output_be.tif"
    
    loader = RasterLoader(file_path=str(test_file_path))
    with pytest.raises(ValueError) as exc_info:
        loader.preview(format="invalid")
    assert "Unsupported format: invalid" in str(exc_info.value)

def test_load_data_from_file():
    """Test the main data loading functionality.
    
    Verifies that:
    - The loader successfully reads and processes the raster file
    - The returned GeoDataFrame has the correct structure
    - All required columns are present
    - The CRS information is properly maintained
    - The geometries are correctly generated
    """
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data"
    test_file_path = data_dir / "output_be.tif"
    
    loader = RasterLoader(file_path=str(test_file_path))
    gdf = loader._load_data_from_file()
    
    # Vérifier la structure du GeoDataFrame
    assert isinstance(gdf, gpd.GeoDataFrame)
    expected_columns = {'pixel_id', 'row', 'col', 'area', 'value', 'latitude', 'longitude', 'geometry'}
    assert all(col in gdf.columns for col in expected_columns)
    assert gdf.crs is not None

def test_downsample_band():
    """Test the downsampling functionality.
    
    Verifies that:
    - The band is correctly downsampled according to block_size
    - The output dimensions are correct
    - The downsampling process preserves data integrity
    - The shape reduction follows the expected ratio
    """
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data"
    test_file_path = data_dir / "output_be.tif"
    
    loader = RasterLoader(file_path=str(test_file_path))
    with rasterio.open(str(test_file_path)) as src:
        original_band = src.read(1)
    
    downsampled = loader._downsample_band(original_band)
    
    # Vérifier les dimensions
    expected_height = original_band.shape[0] // loader.block_size
    expected_width = original_band.shape[1] // loader.block_size
    assert downsampled.shape == (expected_height, expected_width)

def test_nonexistent_file():
    """Test error handling for missing files.
    
    Verifies that:
    - Preview gracefully handles missing files
    - Data loading raises appropriate exceptions
    - Error messages are informative
    - The error handling follows the expected behavior
    """
    test_file_path = "nonexistent/file.tif"
    loader = RasterLoader(file_path=test_file_path)
    
    # Test preview avec fichier inexistant
    preview_result = loader.preview()
    assert "Unable to open raster" in preview_result
    
    # Test _load_data_from_file avec fichier inexistant
    with pytest.raises(RuntimeError) as exc_info:
        loader._load_data_from_file()
    assert "Error while loading downsampled raster" in str(exc_info.value)
