from ..abc_loader import LoaderBase
import rasterio  # To read raster files
from typing import Any  # For type annotation in preview


class RasterLoader(LoaderBase):
    """
    Loader for raster files (GeoTIFF, TIFF, etc.).

    This loader allows loading raster files and quickly previewing their properties.
    It uses the rasterio library for reading files.

    Attributes:
        file_path (str): Path to the raster file to load.
        data (numpy.ndarray): Array containing the loaded raster data.
        meta (dict): Raster metadata (dimensions, CRS, etc.).
        bounds (tuple): Geographic extent of the raster as (left, bottom, right, top).

    Example:
        >>> rst_loader = (
                mapper
                .loader # From the loader module
                .from_file("file_path.tif") # To update with your own path
            )
        >>> rst = rst_loader.load() # Load the data, metadata and bounds and return data 
        >>> meta = rst_loader._instance.meta
        >>> bounds = rst_loader._instance.bounds    
        >>> data = rst[0]  
    """
    def __init__(
        self,
        file_path: str,
        latitude_column=None,
        longitude_column=None,
        coordinate_reference_system=None,
        map_columns=None,
        **kwargs
    ):
        super().__init__(file_path)
        # Other parameters are ignored but accepted for compatibility


    def _load_data_from_file(self) -> Any:
        """
        Load raster data from file and store metadata.

        Returns:
            numpy.ndarray: The loaded raster data (numpy array). It is a 3D array with shape (bands, height, width).
        
        Encapsulates the raster data loading process using rasterio :
         - self.data: Contains the raster data as a numpy array.(which is returned)
         - self.meta: Contains metadata about the raster as a dictionnary with keys :  
            - driver : file format (e.g., 'GTiff')
            - dtype : data type of the raster values (e.g., 'uint16')
            - nodata : value for missing data (e.g., 0)
            - width : width of the raster in pixels
            - height : height of the raster in pixels
            - count : number of bands in the raster
            - CRS : coordinate reference system (e.g., 'EPSG:4326')
            - transform  : affine transformation matrix for georeferencing
        - self.bounds: Contains the geographic extent of the raster as a tuple (left, bottom, right, top).

        NB : 
        - The loader only return data but the metadate and bounds are stored in the instance for later use (cf example in docstring upper).
        Raises:
            RuntimeError: If the raster file cannot be read or is invalid.

        """
        try:
            # Open the raster file with rasterio
            with rasterio.open(self.file_path) as src:
                # Read all raster bands
                self.data = src.read()
                # Store raster metadata
                self.meta = src.meta
                # Store raster bounds ie geographic extent (left, bottom, right, top)
                self.bounds = src.bounds
            # Return raster data
            return self.data
        except Exception as e:
            # In case of error, raise an exception with an explicit message
            raise RuntimeError(f"Error while loading raster: {e}")

    def preview(self, format: str = "ascii") -> Any:
        """
        Generates a preview of the loaded raster information.

        Args:
            format (str): Output format ("ascii" for text display, "json" for dictionary).

        Returns:
            str or dict: A summary of the raster properties.

        Raises:
            ValueError: If the requested format is not supported.

        Example:
            >>> loader = RasterLoader(file_path="my_raster.tif")
            >>> loader._load_data_from_file()
            >>> print(loader.preview())
        """
        # If metadata is not loaded, try to load it
        if self.meta is None:
            try:
                with rasterio.open(self.file_path) as src:
                    self.meta = src.meta
            except Exception as e:
                return f"Unable to open raster: {e}"

        # Get main raster information
        shape = (
            self.meta.get("count", "?"),
            self.meta.get("height", "?"),
            self.meta.get("width", "?")
        )
        dtype = self.meta.get("dtype", "?")
        crs = self.meta.get("crs", "?")

        # Return preview according to requested format
        if format == "ascii":
            return (
                f"Loader: RasterLoader\n"
                f"  File: {self.file_path}\n"
                f"  Dimensions (bands, height, width): {shape}\n"
                f"  Data type: {dtype}\n"
                f"  CRS: {crs}"
            )
        elif format == "json":
            return {
                "loader": "RasterLoader",
                "file": self.file_path,
                "shape": shape,
                "dtype": str(dtype),
                "crs": str(crs)
            }
        else:
            raise ValueError(f"Unsupported format: {format}")


