import geopandas as gpd
from beartype import beartype
from typing import Any

from urban_mapper.modules.loader.loaders.file_loader import FileLoaderBase
from .dataframe_loader import DataFrameLoader

@beartype
class GeoJSONLoader(FileLoaderBase):
    """Loader for `GeoJSON` files containing spatial data.

    This loader reads data from `GeoJSON` files and converts them to `GeoDataFrames` with point geometries.

    Attributes:
        file_path (Path): Path to the `GeoJSON` file to load.
        additional_geometry_columns (Union[str, List[str]]): Name or List of names of other column containing geometry data in WKT format.
        coordinate_reference_system (Union[str, Tuple[str, str]]):
            If a string, it specifies the coordinate reference system to use (default: 'EPSG:4326').
            If a tuple (source_crs, target_crs), it defines a conversion from the source CRS to the target CRS (default target CRS: 'EPSG:4326').

    Examples:
        >>> from urban_mapper.modules.loader import GeoJsonLoader
        >>>
        >>> # Basic usage with lat/long
        >>> loader = GeoJSONLoader(
        ...     file_path="construction.geojson",
        ... )
        >>> gdf = loader.load()
        >>>
        >>> # With CRS
        >>> loader = GeoJSONLoader(
        ...     file_path="construction.geojson",
        ...     coordinate_reference_system="EPSG:4326"
        ... )
        >>> gdf = loader.load()
        >>>
        >>> # With source-target CRS
        >>> loader = GeoJSONLoader(
        ...     file_path="construction.geojson",
        ...     coordinate_reference_system=("EPSG:4326", "EPSG:3857")
        ... )
        >>> gdf = loader.load()
    """

    def _load(self) -> gpd.GeoDataFrame:
        """Load data from a GeoJSON file and convert it to a `GeoDataFrame`.

        This method reads a `GeoJSON` file using geopandas, using the specified coordinate reference system.

        Returns:
            A `GeoDataFrame` containing the loaded data with point geometries
            created from the latitude and longitude columns.

        Raises:
        """
        dataframe = gpd.read_file(self.file_path)

        self.additional_loader_parameters.pop("input_dataframe")

        dataframe_loader = DataFrameLoader(
            input_dataframe=dataframe,
            coordinate_reference_system=self.coordinate_reference_system,
            **self.additional_loader_parameters,
        )

        return dataframe_loader.load()

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this `GeoJSON` loader.

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
        if format == "ascii":
            return (
                f"Loader: GeoJSONLoader\n"
                f"  File: {self.file_path}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Additional params: {self.additional_loader_parameters}\n"
            )
        elif format == "json":
            return {
                "loader": "GeoJSONLoader",
                "file": self.file_path,
                "crs": self.coordinate_reference_system,
                "additional_params": self.additional_loader_parameters,
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
