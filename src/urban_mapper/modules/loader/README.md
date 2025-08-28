# Raster Loaders Directory

⚠️ **Important Note**: This branch contains the development of the raster loader tool that I developed during my internship. However, please note that I have only included the following in this branch: the different versions of the loaders, interesting examples in notebooks, unit tests, and a few readme files.
It therefore does not represent all the work I did during my internship and is not sufficiently explanatory. It just allows you to have all the code to compile directly in the UrbanMapper environment so that you can compile and execute it. 
In fact, I have also created a GitHub repository containing much more detail, namely: all the code present here, other code of interest to the project, my internship report, my overview, a literature review, detailed readme files for everything, the data used in my notebooks, the requirements, etc.
This repository is available at the following [address] (https://github.com/JUDITH-sketch/Rasters_Studies_for_UrbanMapper-OSCUR/blob/main/README.md)

The rest of the files of UrbanMapper remain unchanged for the rasters branch.


## File Descriptions and Evolution

### Core Files

- **loader_factory.py**: Main factory class handling loader instantiation and configuration. Provides a unified interface for loading different data types, including raster files. It manages CRS conversion, column mapping, and supports various file formats. Used by UrbanMapper to create appropriate loaders based on file type.


### Tests Directory

The `tests/` directory contains comprehensive unit tests ensuring the reliability and correctness of the raster loader implementations:

- **test_raster_loader_v2.py**
- **test_raster_loader_v3.py**
- **test_raster_loader_v4.py**
- **test_raster_loader_v5.py**
- **test_raster_loader_v6.py**

### Loader Version Evolution

- **raster_loader_v1**: Initial version with comprehensive functionality planning. Aimed to support multiple raster formats (GeoTIFF, JPEG2000, PNG with world files) and various conversion strategies (points, polygons, contours). Included advanced features like sampling factor control, band selection, and NoData handling. However, this version was too ambitious and complex for initial implementation, leading to a simplified approach in v2.

- **raster_loader_v2**: First version of raster_loader.py file. Many unused (unimplemented) functions were later removed to keep only the three basic loader functions: init, load_from_file, and preview. Initially aimed to handle PNG files but focused on .tif files first. The loader only returns a metadata dictionary.

- **raster_loader_v3**: Second fully functional version of the loader. Only handles .tif files. Returns raster data as a 3D array (containing all bands, not just the first one). Tested in the examples: 1-Per-Module cell.

- **raster_loader_v4**: Third version of the loader. Not yet functional as it doesn't handle large .tif files due to heavy and unoptimized implementation causing infinite loops (no memory issue display, making it impossible to run without manual cell closure). Returns a GDF containing a representation of each raster pixel with number, column, row, latitude and longitude of the pixel center (obtained using transformation matrix and rasterio function) and geometry chosen as a square with pixel bounds coordinates (left, right, top, bottom) also calculated using transformation matrix. Area is also calculated. Finally, a column contains the data value (for the first band). This implementation of the raster returning a GDF to represent data is very naive, iterative, and poorly optimized as it literally loops through pixels and performs each calculation described above for each pixel.

- **raster_loader_v5**: Fourth version of the loader. Returns exactly the same as the previous loader but with optimized calculations. This version is optimized. Calculations use an optimized version that's less iterative and uses package-specific functions to optimize computations. However, even this version didn't produce results due to "Memory Issue", but at least this time the message appears so we know it's because of that, while for the previous one the message didn't even appear - the cell just kept running indefinitely until we manually paused it.

- **raster_loader_v6**: Fifth version of the loader. Starts by downsampling the raster to obtain an aggregated version using the mean function for smoothing. Each block is a block grouping block_size*block_size pixels and takes the average of the contained pixel values. Although this method compresses the raster and changes resolution, it allowed us to overcome the memory issue and encapsulate raster pixels in a GDF. The return is the same as raster_loader_v4. After modifying the factory by adding a with_options method, we can choose the resolution (set to 10 by default) directly at loading time.

## Important Note on Version Usage

To use a specific version of the raster loader, you need to copy the code from the desired version in the versions directory and paste it into the "raster_loader.py" file. By default, the "raster_loader.py" file contains the implementation of raster_loader_v6 (the latest version). This allows you to switch between different implementations while maintaining the same interface.

## Usage Guide

### For Users

1. **Installation**:
```bash
pip install urban-mapper
```

2. **Basic Usage**:
```python
import urban_mapper as um

# Initialize UrbanMapper
mapper = um.UrbanMapper()

# Load a raster file with default settings (block_size=10)
rst_loader = (
    mapper
    .loader
    .from_file("path/to/your/raster.tif")
)
data = rst_loader.load()

# Load with custom block size for different resolution
rst_loader = (
    mapper
    .loader
    .from_file("path/to/your/raster.tif")
    .with_options(block_size=100)  # Larger blocks = lower resolution but faster
)
data = rst_loader.load()
```

3. **Visualization**:
```python
# Static visualization
fig_static = (
    mapper
    .visual
    .with_type("Static")
    .show(columns=["value"])
    .render(data)
)

# Interactive visualization
fig_interactive = (
    mapper
    .visual
    .with_type("Interactive")
    .with_style({"tiles": "CartoDB dark_matter"})
    .show(columns=["value"])
    .render(data)
)
```

## Additional Resources

- [UrbanMapper Documentation](https://urbanmapper.readthedocs.io/)
- [Rasterio Documentation](https://rasterio.readthedocs.io/)
- [OSCUR Project](https://oscur.org/)

