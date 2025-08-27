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

    Attributes:
        file_path (str): Path to the raster file to load.
        gdf (geopandas.GeoDataFrame): GeoDataFrame where each row is a pixel (with geometry, area, coordinates, and value).
        meta (dict): Raster metadata (dimensions, CRS, etc.).

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
    
    Raises : 
        RuntimeError: If there is an error while loading the raster file.
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
            # Open the raster file with rasterio
            with rasterio.open(self.file_path) as src:
                band1 = src.read(1)  # Read the first band
                transform = src.transform # Affine transformation matrix
                raster_crs = src.crs # Coordinate Reference System
                height, width = band1.shape # (height, width)
                nodata_value = src.nodata # Get NoData value from metadata
                
                self.meta = src.meta  # Store metadata for later use
                self.bounds = src.bounds  # Store bounds for later use
            
            # Prepare lists to store pixel data
            pixel_ids = []
            rows = []
            cols = []
            areas = []
            lats = []
            lons = []
            values = []
            polygons = []

            # Prepare transformer for CRS conversion (if needed). The difference between geographic and projected CRS is that geographic CRS uses latitude and longitude, while projected CRS uses a flat coordinate system (like meters).
            crs_is_geographic = CRS.from_user_input(raster_crs).is_geographic
            
            if crs_is_geographic:
                # Use EPSG:3857 (Web Mercator) for area calculation
                metric_crs = CRS.from_epsg(3857)
                transformer_to_metric = Transformer.from_crs(raster_crs, metric_crs, always_xy=True)
                transformer_to_wgs84 = Transformer.from_crs(raster_crs, "EPSG:4326", always_xy=True)
            else:
                metric_crs = raster_crs
                transformer_to_wgs84 = Transformer.from_crs(raster_crs, "EPSG:4326", always_xy=True)
                        
            pixel_id = 0

            for row in range(height):
                for col in range(width):
                    
                    value = band1[row, col]
                     # Check for NoData (handles both nodata_value and NaN)
                    if nodata_value is not None and value == nodata_value:
                        value_out = None
                    elif np.isnan(value):
                        value_out = None
                    else:
                        value_out = value

                    if np.isnan(value):
                        continue

                    # Compute the coordinates of the four corners of the pixel
                    # Upper left
                    ulx, uly = xy(transform, row, col, offset='ul')
                    # Upper right
                    urx, ury = xy(transform, row, col + 1, offset='ul')
                    # Lower right
                    lrx, lry = xy(transform, row + 1, col + 1, offset='ul')
                    # Lower left
                    llx, lly = xy(transform, row + 1, col, offset='ul')

                    # Build the polygon (in raster CRS)
                    poly = Polygon([(ulx, uly), (urx, ury), (lrx, lry), (llx, lly)])

                    # Compute the area in m²
                    if crs_is_geographic:
                        # Reproject polygon to metric CRS for area calculation
                        poly_metric = gpd.GeoSeries([poly], crs=raster_crs).to_crs(metric_crs).iloc[0]
                        area_m2 = poly_metric.area
                    else:
                        area_m2 = poly.area

                    # Compute centroid for lat/lon
                    centroid_x, centroid_y = poly.centroid.x, poly.centroid.y
                    lon, lat = transformer_to_wgs84.transform(centroid_x, centroid_y)

                    # Store data
                    pixel_ids.append(pixel_id)
                    rows.append(row)
                    cols.append(col)
                    areas.append(area_m2)
                    lats.append(lat)
                    lons.append(lon)
                    values.append(value_out)
                    polygons.append(poly)
                    pixel_id += 1
            
            # Build the GeoDataFrame
            gdf = gpd.GeoDataFrame({
                "pixel_id": pixel_ids,
                "row": rows,
                "col": cols,
                "area": areas,
                "latitude": lats,
                "longitude": lons,
                "value": values,
                "geometry": polygons
            }, crs=raster_crs)

            # Store for direct display
            self.gdf = gdf

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


