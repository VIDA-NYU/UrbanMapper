# Tests Directory

⚠️ **Important Note**: This branch contains the development of the raster loader tool that I developed during my internship. However, please note that I have only included the following in this branch: the different versions of the loaders, interesting examples in notebooks, unit tests, and a few readme files.
It therefore does not represent all the work I did during my internship and is not sufficiently explanatory. It just allows you to have all the code to compile directly in the UrbanMapper environment so that you can compile and execute it. 
In fact, I have also created a GitHub repository containing much more detail, namely: all the code present here, other code of interest to the project, my internship report, my overview, a literature review, detailed readme files for everything, the data used in my notebooks, the requirements, etc.
This repository is available at the following [address] (https://github.com/JUDITH-sketch/Rasters_Studies_for_UrbanMapper-OSCUR/blob/main/README.md)

## Directory Overview

This directory contains unit tests for the raster loader implementations. The tests ensure proper functionality and reliability of the raster data handling capabilities.

## Directory Structure
```
tests/
├── test_raster_loader_v2.py    # Tests for version 2 of the loader
├── test_raster_loader_v3.py    # Tests for version 3 of the loader
├── test_raster_loader_v4.py    # Tests for version 4 of the loader
├── test_raster_loader_v5.py    # Tests for version 5 of the loader
└── test_raster_loader_v6.py    # Tests for version 6 of the loader
```

## Test Files Description

### test_raster_loader_v2.py

Tests the basic functionality of the RasterLoader class:
- Initialization of RasterLoader
- Parameter setters functionality
- Error handling for missing files
- GeoTIFF file loading capabilities

Key test cases:
```python
# Test loader initialization
test_raster_loader_initialization()

# Test parameter setters
test_raster_loader_setters()

# Test error handling
test_raster_loader_load_missing_file()

# Test GeoTIFF loading
test_geotiff_loading()
```

### test_raster_loader_v3.py

Tests the 3D array output functionality:
- Proper loading of all bands
- Array shape verification
- Data type validation
- Band count verification

### test_raster_loader_v4.py

Tests the GeoDataFrame conversion features:
- Pixel to point conversion
- Coordinate transformation
- Geometry creation
- Attribute calculation (area, row, column)
- Value assignment from first band

### test_raster_loader_v5.py

Tests the optimized GeoDataFrame conversion:
- Memory usage optimization
- Vectorized calculations
- Performance benchmarks
- Error handling for large files

### test_raster_loader_v6.py

Tests the downsampling functionality:
- Block size parameter validation
- Mean value calculation
- Resolution reduction
- Memory efficiency
- Options configuration through factory

## Running Tests

1. **Prerequisites**:
   - Python 3.7+
   - pytest installed (`pip install pytest`)
   - urban_mapper installed
   - Access to test data files

2. **Running all tests**:
```bash
# From the Raster Loaders directory
pytest tests/ -v
```

3. **Running specific tests**:
```bash
# Run a specific test file
pytest tests/test_raster_loader_v2.py -v

# Run a specific test case
pytest tests/test_raster_loader_v2.py::test_geotiff_loading -v
```

4. **Running with detailed output**:
```bash
pytest tests/test_raster_loader_v2.py -v --capture=no
```

## Adding New Tests

1. Create a new test file following the naming convention:
```python
test_raster_loader_v[X].py  # Where X is the version number
```

2. Structure your tests:
```python
def test_new_feature():
    # Test setup
    loader = RasterLoader("test_file.tif")
    
    # Test execution
    result = loader.new_feature()
    
    # Assertions
    assert result == expected_value
```

3. Add any necessary test data to the `data/` directory

## Test Data

The test data required for running these tests (such as `output_be.tif` for `test_raster_loader_v2.py`) can be found in the main project's `/Data` directory.

To run the tests:
1. Make sure you have access to the raster files in the project's `/Data` directory
2. The test files will automatically look for the required data in this location
3. If using different test data, update the file paths in the test files accordingly


## Troubleshooting

If tests fail:
1. Check that all dependencies are installed
2. Verify test data files are present in the correct location
3. Ensure urban_mapper is installed and accessible
4. Check file permissions for test data access

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Test Coverage Report](Not available in this repository - see forked branch)
- [Contributing Guidelines](See main UrbanMapper repository)
