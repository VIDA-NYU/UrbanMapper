import pandas as pd
import geopandas as gpd
from shapely import wkt
from beartype import beartype
from typing import Union, Optional, Any, Tuple

from urban_mapper.modules.loader.abc_loader import LoaderBase
from urban_mapper.config import DEFAULT_CRS


@beartype
class DataFrameLoader(LoaderBase):
    """Loader for `DataFrame` object containing spatial data.

    This loader reads data from a  pandas `DataFrame` object and
    converts them to `GeoDataFrames` with point geometries. It requires latitude
    and longitude columns to create point geometries for each row.

    Attributes:
        input_dataframe (DataFrame): Original DataFrame object.
        latitude_column (str): Name of the column containing latitude values.
        longitude_column (str): Name of the column containing longitude values.
        geometry_column (str): Name of the column containing geometry data in WKT format.
        coordinate_reference_system (Union[str, Tuple[str, str]]):
            If a string, it specifies the coordinate reference system to use (default: 'EPSG:4326').
            If a tuple (source_crs, target_crs), it defines a conversion from the source CRS to the target CRS (default target CRS: 'EPSG:4326').

    Examples:
        >>> from urban_mapper.modules.loader import DataFrameLoader
        >>>
        >>> # Load/create a `dataframe` object
        ...
        >>> # Basic usage with lat/long
        >>> loader = DataFrameLoader(
        ...     input_dataframe=dataframe,
        ...     latitude_column="pickup_lat",
        ...     longitude_column="pickup_lng"
        ... )
        >>> gdf = loader.load()
        >>>
        >>> # Basic usage with geometry
        >>> loader = DataFrameLoader(
        ...     input_dataframe=dataframe,
        ...     geometry_column="the_geom"
        ... )
        >>> gdf = loader.load()
        >>>
        >>> # With custom separator and encoding
        >>> loader = DataFrameLoader(
        ...     input_dataframe=dataframe,
        ...     geometry_column="geom",
        ...     separator=";",
        ...     encoding="latin-1"
        ... )
        >>> gdf = loader.load()
        >>>
        >>> # With CRS
        >>> loader = DataFrameLoader(
        ...     input_dataframe=dataframe,
        ...     latitude_column="lat",
        ...     longitude_column="lng",
        ...     coordinate_reference_system="EPSG:4326"
        ... )
        >>> gdf = loader.load()
        >>>
        >>> # With source-target CRS
        >>> loader = DataFrameLoader(
        ...     input_dataframe=dataframe,
        ...     latitude_column="lat",
        ...     longitude_column="lng",
        ...     coordinate_reference_system=("EPSG:4326", "EPSG:3857")
        ... )
        >>> gdf = loader.load()
    """

    def __init__(
        self,
        input_dataframe: Union[pd.DataFrame, gpd.GeoDataFrame],
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        geometry_column: Optional[str] = None,
        coordinate_reference_system: Union[str, Tuple[str, str]] = DEFAULT_CRS,
        **additional_loader_parameters: Any,
    ) -> None:
        super().__init__(
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            geometry_column=geometry_column,
            coordinate_reference_system=coordinate_reference_system,
            **additional_loader_parameters,
        )
        self.dataframe = input_dataframe.copy()

    def _load(self) -> gpd.GeoDataFrame:
        """Load spatial data from a dataframe.

        This is the main public method for using `loaders`. It performs validation
        on the inputs before delegating to the implementation-specific `_load` method.
        It also ensures the file exists and that the coordinate reference system is properly set.

        Returns:
            A `GeoDataFrame` containing the loaded spatial data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If required columns are missing or the file format is invalid.

        Examples:
            >>> from urban_mapper.modules.loader import DataFrameLoader
            >>> loader = DataFrameLoader(dataframe, latitude_column="pickup_lat", longitude_column="pickup_lng")
            >>> gdf = loader.load()
        """
        if isinstance(self.dataframe, gpd.GeoDataFrame):
            geo_dataframe: gpd.GeoDataFrame = self.dataframe
        else:
            if self.latitude_column != "" and self.longitude_column != "":
                # Ensure latitude and longitude columns are numeric
                self.dataframe[self.latitude_column] = pd.to_numeric(
                    self.dataframe[self.latitude_column], errors="coerce"
                )
                self.dataframe[self.longitude_column] = pd.to_numeric(
                    self.dataframe[self.longitude_column], errors="coerce"
                )
                geometry = gpd.points_from_xy(
                    self.dataframe[self.longitude_column],
                    self.dataframe[self.latitude_column],
                )
            else:
                filter_not_na = self.dataframe[self.geometry_column].notna()
                self.dataframe.loc[filter_not_na, self.geometry_column] = (
                    self.dataframe.loc[filter_not_na, self.geometry_column].apply(
                        wkt.loads
                    )
                )
                geometry = self.geometry_column

            geo_dataframe = gpd.GeoDataFrame(
                self.dataframe,
                geometry=geometry,
                crs=self.coordinate_reference_system[0]
                if isinstance(self.coordinate_reference_system, tuple)
                else self.coordinate_reference_system,
            )

        target_coordinate_reference_system = (
            self.coordinate_reference_system[1]
            if isinstance(self.coordinate_reference_system, tuple)
            else self.coordinate_reference_system
        )

        if geo_dataframe.crs is None:
            geo_dataframe.set_crs(target_coordinate_reference_system, inplace=True)
        elif geo_dataframe.crs.to_string() != target_coordinate_reference_system:
            geo_dataframe = geo_dataframe.to_crs(target_coordinate_reference_system)

        return geo_dataframe

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this `DataFrameLoader` loader.

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
                f"Loader: DataFrameLoader\n"
                f"  Latitude Column: {self.latitude_column}\n"
                f"  Longitude Column: {self.longitude_column}\n"
                f"  Geometry Column: {self.geometry_column}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Additional params: {self.additional_loader_parameters}\n"
            )
        elif format == "json":
            return {
                "loader": "DataFrameLoader",
                "latitude_column": self.latitude_column,
                "longitude_column": self.longitude_column,
                "geometry_column": self.geometry_column,
                "crs": self.coordinate_reference_system,
                "additional_params": self.additional_loader_parameters,
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
