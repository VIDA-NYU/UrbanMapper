from ..abc_loader import LoaderBase
import rasterio  # To read raster files
from typing import Any  # For type annotation in preview
import numpy as np  
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import box  
from rasterio.transform import xy
from pyproj import CRS,Transformer

class RasterLoader(LoaderBase):
    
    """
    Loader for raster files (GeoTIFF, PNG+world file, etc.).

    This loader reads raster files and exposes their content as a GeoDataFrame where each row represents a pixel as a polygon.
    It allows fast preview of raster properties, pixel-wise spatialization, and direct integration with the UrbanMapper factory.
    It's an optimized version of RasterLoader with gdf return.

    Attributes:
        file_path (str): Path to the raster file to load.
        gdf (geopandas.GeoDataFrame): GeoDataFrame where each row is a pixel (with geometry, area, coordinates, and value).
        meta (dict): Raster metadata (dimensions, CRS, etc.).
        bounds (tuple): Geographic extent of the raster as (left, bottom, right, top).

    Example:
         >>> rst_loader = (
                mapper
                .loader # From the loader module
                .from_file("file_path.tif") # To update with your own path
            )
        >>> gdf = rst_loader.load() # Load the data and return data 
        >>> gdf       
        >>> meta = rst_loader._instance.meta
        >>> bounds = rst_loader._instance.bounds
    
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

    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        """
        Loads raster data and returns a GeoDataFrame where each row represents a pixel as a polygon.
        NoData pixels are included with value set to None.

        Returns :
        -------
            gpd.GeoDataFrame
            A GeoDataFrame with columns: pixel_id, row, col, area, latitude, longitude, value, geometry.
        Raises:
            RuntimeError: If there is an error while loading the raster file.  
        NB : the loader doesn't return metadata and bounds, but they are stored in the instance attributes (cf docstring example).           
        """
        try:
            with rasterio.open(self.file_path) as src:         
                band = src.read(1)
                transform = src.transform
                crs = src.crs
                nodata = src.nodata
                height, width = band.shape

                self.meta = src.meta  # Store metadata for later use
                self.bounds = src.bounds  # Store bounds for later use

            # Flatten indices
            rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
            rows_flat = rows.ravel()
            cols_flat = cols.ravel()
            values_flat = band.ravel()
            
            # Handle nodata
            if nodata is not None:
                values_flat = np.where(values_flat == nodata, None, values_flat)
        
            # Compute pixel bounds (vectorized)
            x_min, y_max = rasterio.transform.xy(transform, rows_flat, cols_flat, offset='ul')
            x_max, y_min = rasterio.transform.xy(transform, rows_flat, cols_flat, offset='lr')
    
            # Create polygons
            polygons = [box(xmin, ymin, xmax, ymax) for xmin, ymin, xmax, ymax in zip(x_min, y_min, x_max, y_max)]
    
            # Build GeoDataFrame
            gdf = gpd.GeoDataFrame({
                'pixel_id': np.arange(len(values_flat)),
                'row': rows_flat,
                'col': cols_flat,
                'value': values_flat,
                'geometry': polygons
            }, crs=crs)
    
            # Calculate pixel area (projected CRS)
            if CRS.from_user_input(crs).is_projected:
                pixel_area = abs(transform.a * transform.e)
                gdf['area'] = pixel_area
            else:
                # Reproject polygons to a metric CRS for area calculation
                metric_crs = CRS.from_epsg(3857)
                gdf_metric = gdf.to_crs(metric_crs)
                gdf['area'] = gdf_metric.geometry.area
    
            # Compute centroid lat/lon in batch
            centroids = gdf.geometry.centroid
            transformer = Transformer.from_crs(crs, 'EPSG:4326', always_xy=True)
            lon, lat = transformer.transform(centroids.x.values, centroids.y.values)
            gdf['longitude'] = lon
            gdf['latitude'] = lat
    
            return gdf
        
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


