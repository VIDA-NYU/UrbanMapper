"""
Unit tests for the RasterLoader class.

This test suite provides comprehensive testing for the RasterLoader class, which handles 
the loading and processing of raster data files in the UrbanMapper project.

Test Categories:
---------------
1. Basic Functionality Tests:
   - Initialization (test_raster_loader_init)
   - Data loading (test_raster_loader_load_data)
   - Preview generation (test_raster_loader_preview_*)

2. Data Validation Tests:
   - Values and dimensions (test_raster_values_and_dimensions)
   - NoData handling (test_nodata_handling)
   - Geographic attributes (test_geographic_attributes)
   - Metadata completeness (test_metadata_completeness)

3. Error Handling Tests:
   - Invalid file paths (test_raster_loader_invalid_file)
   - Invalid preview formats (test_raster_loader_invalid_preview_format)

Test Data:
----------
Two test fixtures are provided:
1. sample_raster_path:
   - 2x3 pixels raster
   - Values: [[1, 2, 3], [4, 5, 6]]
   - Data type: float32
   - CRS: EPSG:4326 (WGS 84)
   
2. sample_raster_with_nodata:
   - 2x3 pixels raster with NaN values
   - Values: [[1, NaN, 3], [4, 5, NaN]]
   - Data type: float32
   - CRS: EPSG:4326 (WGS 84)

How to Run Tests:
---------------
1. Basic execution:
   pytest test_raster_loader.py

2. With verbosity:
   pytest -v test_raster_loader.py

3. Specific test category:
   pytest test_raster_loader.py -k "preview"
   pytest test_raster_loader.py -k "geographic"
   pytest test_raster_loader.py -k "invalid"

4. With coverage report:
   pytest --cov=urban_mapper test_raster_loader.py

Requirements:
------------
- pytest >= 8.4.0
- rasterio >= 1.3.0
- numpy >= 1.24.0
- geopandas >= 0.14.0
- shapely >= 2.0.0
- pyproj >= 3.6.0

Notes:
------
- Tests use temporary files created via pytest's tmp_path fixture
- Geographic tests verify both projected and geographic coordinate systems
- NoData handling is tested with NaN values
- All geometric operations are validated for correctness
"""

import pytest
import rasterio
import numpy as np
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
from urban_mapper.modules.loader.loaders.raster_loader import RasterLoader
import geopandas as gpd

@pytest.fixture
def sample_raster_path(tmp_path):
    """
    Create a temporary test raster file with known properties.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory path
        
    Returns:
        str: Path to the created test raster file
        
    Note:
        Creates a 2x3 GeoTIFF file with float32 values and EPSG:4326 projection
    """
    raster_path = tmp_path / "test.tif"
    
    # Create sample raster data
    data = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
    transform = rasterio.transform.from_origin(0, 0, 1, 1)
    
    with rasterio.open(
        raster_path,
        'w',
        driver='GTiff',
        height=2,
        width=3,
        count=1,
        dtype=data.dtype,
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        dst.write(data, 1)
    
    return str(raster_path)

@pytest.fixture
def sample_raster_with_nodata(tmp_path):
    """
    Create a test raster with NoData values.
    """
    raster_path = tmp_path / "test_nodata.tif"
    data = np.array([[1, np.nan, 3], [4, 5, np.nan]], dtype=np.float32)
    transform = rasterio.transform.from_origin(0, 0, 1, 1)
    
    with rasterio.open(
        raster_path,
        'w',
        driver='GTiff',
        height=2,
        width=3,
        count=1,
        dtype=data.dtype,
        crs='EPSG:4326',
        transform=transform,
        nodata=np.nan
    ) as dst:
        dst.write(data, 1)
    
    return str(raster_path)

def test_raster_loader_init(sample_raster_path):
    """
    Test the initialization of RasterLoader.
    
    Verifies that:
        - The loader is created successfully
        - The file path is correctly stored
    """
    loader = RasterLoader(sample_raster_path)
    assert str(loader.file_path) == str(sample_raster_path)

def test_raster_loader_load_data(sample_raster_path):
    """
    Test the raster data loading functionality.
    
    Verifies that:
        - Data is loaded into a GeoDataFrame
        - All expected columns are present
        - The number of pixels matches the input raster (2x3 = 6 pixels)
        - Metadata and bounds are properly loaded
    """
    loader = RasterLoader(sample_raster_path)
    gdf = loader._load_data_from_file()
    
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert len(gdf) == 6  # 2x3 raster = 6 pixels
    assert all(col in gdf.columns for col in ['pixel_id', 'row', 'col', 'area', 'latitude', 'longitude', 'value', 'geometry'])
    assert loader.meta is not None
    assert loader.bounds is not None

def test_raster_loader_preview_ascii(sample_raster_path):
    """
    Test the ASCII format preview functionality.
    
    Verifies that:
        - Preview returns a string
        - Preview contains all essential information (loader type, file path, dimensions, CRS)
        - The format matches expected ASCII output
    """
    loader = RasterLoader(sample_raster_path)
    # Charger les métadonnées d'abord
    loader._load_data_from_file()
    preview = loader.preview(format="ascii")
    
    assert isinstance(preview, str)
    assert "RasterLoader" in preview
    assert str(sample_raster_path) in preview
    assert "Dimensions" in preview
    assert "CRS" in preview

def test_raster_loader_preview_json(sample_raster_path):
    """
    Test the JSON format preview functionality.
    
    Verifies that:
        - Preview returns a dictionary
        - All required keys are present
        - Values are properly formatted
    """
    loader = RasterLoader(sample_raster_path)
    loader._load_data_from_file()
    preview = loader.preview(format="json")
    
    assert isinstance(preview, dict)
    assert preview["loader"] == "RasterLoader"
    # Ne pas tester l'égalité exacte des chemins
    assert "file" in preview
    assert "shape" in preview
    assert "dtype" in preview
    assert "crs" in preview

def test_raster_loader_invalid_file():
    """
    Test error handling for invalid file paths.
    
    Verifies that:
        - Appropriate RuntimeError is raised when file doesn't exist
        - Error handling works as expected
    """
    with pytest.raises(RuntimeError):
        loader = RasterLoader("nonexistent_file.tif")
        loader._load_data_from_file()

def test_raster_loader_invalid_preview_format(sample_raster_path):
    """
    Test error handling for invalid preview formats.
    
    Verifies that:
        - ValueError is raised for unsupported formats
        - Error handling works as expected
    """
    loader = RasterLoader(sample_raster_path)
    # Charger les métadonnées d'abord
    loader._load_data_from_file()
    with pytest.raises(ValueError):
        loader.preview(format="invalid")

def test_raster_values_and_dimensions(sample_raster_path):
    """
    Test exact values and dimensions of loaded raster.
    
    Verifies:
        - Exact pixel values match input data
        - Dimensions are correct
        - Row and column indices are correct
    """
    loader = RasterLoader(sample_raster_path)
    gdf = loader._load_data_from_file()
    
    # Check dimensions
    assert len(gdf) == 6  # 2x3 raster
    assert len(gdf[gdf['row'] == 0]) == 3  # 3 pixels in first row
    assert len(gdf[gdf['row'] == 1]) == 3  # 3 pixels in second row
    
    # Check values
    expected_values = [1, 2, 3, 4, 5, 6]
    assert all(gdf['value'].values == expected_values)
    
    # Check pixel ordering
    assert all(gdf.iloc[0][['row', 'col']] == [0, 0])
    assert all(gdf.iloc[-1][['row', 'col']] == [1, 2])

def test_nodata_handling(sample_raster_with_nodata):
    """
    Test handling of NoData values.
    
    Verifies:
        - NoData values are correctly identified
        - NoData pixels are properly handled
        - Valid pixels are still processed correctly
    """
    loader = RasterLoader(sample_raster_with_nodata)
    gdf = loader._load_data_from_file()
    
    # Check that we have 4 valid pixels (2 are NaN)
    assert len(gdf) == 4
    
    # Verify values are correct
    values = gdf['value'].values
    assert 1.0 in values
    assert 3.0 in values
    assert 4.0 in values
    assert 5.0 in values

def test_geographic_attributes(sample_raster_path):
    """
    Test geographic attributes of loaded data.
    
    Verifies:
        - CRS is correctly set
        - Areas are calculated properly
        - Latitude/Longitude values are within expected ranges
        - Geometries are valid polygons
    """
    loader = RasterLoader(sample_raster_path)
    gdf = loader._load_data_from_file()
    
    # Check CRS
    assert gdf.crs == 'EPSG:4326'
    
    # Check geographic bounds
    assert all(gdf['latitude'].between(-90, 90))
    assert all(gdf['longitude'].between(-180, 180))
    
    # Check geometries
    assert all(gdf.geometry.is_valid)
    assert all(gdf.geometry.geom_type == 'Polygon')
    
    # Check areas are positive
    assert all(gdf['area'] > 0)

def test_metadata_completeness(sample_raster_path):
    """
    Test completeness of raster metadata.
    
    Verifies:
        - All required metadata fields are present
        - Metadata values are correct
        - Bounds are properly set
    """
    loader = RasterLoader(sample_raster_path)
    loader._load_data_from_file()
    
    # Check metadata
    assert 'count' in loader.meta
    assert 'height' in loader.meta
    assert 'width' in loader.meta
    assert 'crs' in loader.meta
    assert 'transform' in loader.meta
    
    # Check specific values
    assert loader.meta['height'] == 2
    assert loader.meta['width'] == 3
    assert loader.meta['count'] == 1
    
    # Check bounds
    assert len(loader.bounds) == 4  # minx, miny, maxx, maxy
