from typing import Any

import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.loader.abc_loader import LoaderBase


@beartype
class ShapefileLoader(LoaderBase):
    """Loader for `shapefiles` containing spatial data.

    This loader reads data from `shapefiles` and returns a `GeoDataFrame`. Shapefiles
    inherently contain geometry information, so explicit latitude and longitude
    columns are not required. However, if specified, they can be used; otherwise,
    `representative points` are generated.

    `Representative points` are a simplified representation of the geometry, which can be
    useful for visualisations or when the geometry is complex. The loader will
    automatically create temporary columns for latitude and longitude if they are not
    provided or if the specified columns contain only `NaN` values.

    Attributes:
        file_path (Union[str, Path]): Path to the `shapefile` to load.
        latitude_column (Optional[str]): Name of the column containing latitude values. If not provided or empty,
            a temporary latitude column is generated from representative points. Default: `None`
        longitude_column (Optional[str]): Name of the column containing longitude values. If not provided or empty,
            a temporary longitude column is generated from representative points. Default: `None`
        coordinate_reference_system (str): The coordinate reference system to use. Default: `EPSG:4326`

    Examples:
        >>> from urban_mapper.modules.loader import ShapefileLoader
        >>>
        >>> # Basic usage
        >>> loader = ShapefileLoader(
        ...     file_path="data.shp"
        ... )
        >>> gdf = loader.load_data_from_file()
        >>>
        >>> # With specified latitude and longitude columns
        >>> loader = ShapefileLoader(
        ...     file_path="data.shp",
        ...     latitude_column="lat",
        ...     longitude_column="lon"
        ... )
        >>> gdf = loader.load_data_from_file()
    """

    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        """Load data from a shapefile and return a `GeoDataFrame`.

        This method reads a `shapefile` using geopandas, ensures it has a geometry column,
        reprojects it to the specified `CRS` if necessary, and handles latitude and
        longitude columns. If latitude and longitude columns are not provided or are
        empty, it generates temporary columns using `representative points` of the geometries.

        Returns:
            A `GeoDataFrame` containing the loaded data with geometries and
            latitude/longitude columns as specified or generated.

        Raises:
            ValueError: If no geometry column is found in the shapefile.
            Exception: If the shapefile cannot be read (e.g., file not found or invalid format).
        """
        gdf = gpd.read_file(self.file_path)

        if "geometry" not in gdf.columns:
            raise ValueError(
                "No geometry column found in shapefile. "
                "Standard shapefile format requires a geometry column."
            )

        if gdf.crs.to_string() != self.coordinate_reference_system:
            gdf = gdf.to_crs(self.coordinate_reference_system)

        if (
            not self.latitude_column
            or not self.longitude_column
            or gdf[self.latitude_column].isna().all()
            or gdf[self.longitude_column].isna().all()
        ):
            gdf["representative_points"] = gdf.geometry.representative_point()
            gdf["temporary_longitude"] = gdf["representative_points"].x
            gdf["temporary_latitude"] = gdf["representative_points"].y
            self.latitude_column = "temporary_latitude"
            self.longitude_column = "temporary_longitude"

        return gdf

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this `CSV` loader.

        Creates a summary representation of the loader for quick inspection.

        Args:
            format: The output format for the preview. Options include:

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use

        Returns:
            A string or dictionary representing the loader, depending on the format.

        Raises:
            ValueError: If an unsupported format is requested.
        """
        lat_col = self.latitude_column or "temporary_latitude (generated)"
        lon_col = self.longitude_column or "temporary_longitude (generated)"

        if format == "ascii":
            return (
                f"Loader: ShapefileLoader\n"
                f"  File: {self.file_path}\n"
                f"  Latitude Column: {lat_col}\n"
                f"  Longitude Column: {lon_col}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Additional params: {self.additional_loader_parameters}\n"
            )
        elif format == "json":
            return {
                "loader": "ShapefileLoader",
                "file": self.file_path,
                "latitude_column": lat_col,
                "longitude_column": lon_col,
                "crs": self.coordinate_reference_system,
                "additional_params": self.additional_loader_parameters,
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
