import pytest
from urban_mapper.modules.loader.loaders.raster_loader import RasterLoader

def test_raster_loader_initialization():
    loader = RasterLoader("fake_path.tif")
    assert str(loader.file_path) == "fake_path.tif"

def test_raster_loader_setters():
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

<<<<<<< HEAD
<<<<<<< HEAD
def test_raster_loader_load_missing_file():
    loader = RasterLoader("fake_path.tif")
    with pytest.raises(RuntimeError) as excinfo:
        loader._load_data_from_file()
    assert "No such file or directory" in str(excinfo.value)

import os

def test_geotiff_loading():

    test_path = os.path.join(os.path.dirname(__file__), "data", "output_be.tif")
    if not os.path.exists(test_path):
        pytest.skip("GeoTIFF for test missing")
    loader = RasterLoader(test_path)
    result = loader._load_data_from_file()
    assert "data_shape" in result
    assert "data_dtype" in result
    assert "crs" in result
    assert "transform" in result


=======
def test_raster_loader_load_not_implemented():
=======
def test_raster_loader_load_missing_file():
>>>>>>> adb60a0 (feat : "test: add functional test for GeoTIFF loading in RasterLoader")
    loader = RasterLoader("fake_path.tif")
    with pytest.raises(RuntimeError) as excinfo:
        loader._load_data_from_file()
<<<<<<< HEAD
>>>>>>> 966824d ("feat: implement basic GeoTIFF loading in RasterLoader with rasterio")
=======
    assert "No such file or directory" in str(excinfo.value)

import os

def test_geotiff_loading():

    test_path = os.path.join(os.path.dirname(__file__), "data", "output_be.tif")
    if not os.path.exists(test_path):
        pytest.skip("GeoTIFF for test missing")
    loader = RasterLoader(test_path)
    result = loader._load_data_from_file()
    assert "data_shape" in result
    assert "data_dtype" in result
    assert "crs" in result
    assert "transform" in result


>>>>>>> adb60a0 (feat : "test: add functional test for GeoTIFF loading in RasterLoader")

