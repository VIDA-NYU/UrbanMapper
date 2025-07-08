from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any, Union
import geopandas as gpd
from beartype import beartype
from pathlib import Path
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import require_attributes_not_none
from urban_mapper import logger


@beartype
class UrbanLayerBase(ABC):
    """Abstract base class for all urban layers

    This abstract class defines the interface that all urban layer implementations
    must follow. Urban layers represent spatial layers (dataset as `GeoDataframe`) used for geographical
    analysis and mapping within `UrbanMapper`, such as `streets`, `regions`, or custom layers.

    Attributes:
        layer (gpd.GeoDataFrame | None): The `GeoDataFrame` containing the spatial data.
        mappings (List[Dict[str, object]]): List of mapping configurations for relating this layer to datasets (bridging layer <-> dataset).
        coordinate_reference_system (str): The coordinate reference system used by this layer. Default: EPSG:4326.
        has_mapped (bool): Indicates whether this layer has been mapped to another dataset.

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> streets = mapper.urban_layer.osmnx_streets().from_place("London, UK")
        >>> # This is an abstract class; use concrete implementations like OSMNXStreets
    """

    def __init__(self) -> None:
        self.layer: gpd.GeoDataFrame | None = None
        self.mappings: List[Dict[str, object]] = []
        self.coordinate_reference_system: str = DEFAULT_CRS
        self.has_mapped: bool = False
        self.data_id: str | None = None

    @abstractmethod
    def from_place(self, place_name: str, **kwargs) -> None:
        """Load an urban layer from a place name

        Creates and populates the layer attribute with spatial data from the specified place.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for geocoding the place name and retrieving the corresponding spatial data.

        Args:
            place_name: Name of the place to load (e.g., "New York City", "Paris, France").
            **kwargs: Additional implementation-specific parameters.
                Common parameters include:

                - [x] network_type: Type of network to retrieve (for street networks)
                - [x] tags: OSM tags to filter features (for OSM-based layers, like cities features)

        Raises:
            ValueError: If the place cannot be geocoded or data cannot be retrieved.
        """
        pass

    @abstractmethod
    def from_file(self, file_path: str | Path, **kwargs) -> None:
        """Load an urban layer from a local file.

        Creates and populates the layer attribute with spatial data from the specified file.

        !!! note "What is the difference between `from_file` and `from_place`?"
            The `from_file` method is used to load spatial data from a local file (e.g., shapefile, GeoJSON), if
            the urban layer is not available through `from_place`, it should be having a fallback to `from_file`.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for reading the file and loading the corresponding spatial data.

        Args:
            file_path: Path to the file containing the spatial data.
            **kwargs: Additional implementation-specific parameters.

        Raises:
            ValueError: If the file cannot be read or does not contain valid spatial data.
            FileNotFoundError: If the specified file does not exist.
        """
        pass

    @abstractmethod
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_element",
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """Map points to their nearest elements in this urban layer.

        Performs spatial joining of points to their nearest elements using either
        provided column names or predefined mappings.

        !!! "How does the mapping / spatial join works?"
            The map nearest layer is based on the type of urban layer,
            e.g `streets roads` will be mapping to the `nearest street`, while `streets sidewalks` will be mapping to
            the `nearest sidewalk`. Or in a nutshell, for any new urban layer, the mapping will be based on
            the type of urban layer.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for performing the spatial join and mapping the points to their nearest elements.

        Args:
            data (gpd.GeoDataFrame): `GeoDataFrame` with points to map.
            longitude_column (str | None, optional): Column name for longitude values.
            latitude_column (str | None, optional): Column name for latitude values.
            output_column (str | None, optional): Column name for mapping results.
            threshold_distance (float | None, optional): Maximum distance for mapping. I.e. if a record is N distance away from urban layer's component, that fits within the threshold distance, it will be mapped to the nearest component, otherwise will be skipped.
            **kwargs: Additional parameters for the implementation.

        Returns:
            Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]: Updated urban layer and mapped data.

        Raises:
            ValueError: If the layer is not loaded, columns are missing, or mappings are invalid.

        Examples:
            >>> mapper = UrbanMapper()
            >>> streets = mapper.urban_layer.osmnx_streets().from_place("Edinburgh, UK")
            >>> _, mapped = streets.map_nearest_layer(
            ...     data=taxi_trips,
            ...     longitude_column="pickup_lng",
            ...     latitude_column="pickup_lat",
            ...     output_column="nearest_street"
            ... )
        """
        pass

    @abstractmethod
    def get_layer(self) -> gpd.GeoDataFrame:
        """Get the `GeoDataFrame` representing this urban layer.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for returning the urban layer data.

        Returns:
            The `GeoDataFrame` containing the urban layer data.

        Raises:
            ValueError: If the layer has not been loaded yet.
        """
        pass

    @abstractmethod
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get the bounding box coordinates of this urban layer.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for calculating the bounding box.

        Returns:
            A tuple containing (`min_x`, `min_y`, `max_x`, `max_y`) coordinates of the bounding box.

        Raises:
            ValueError: If the layer has not been loaded yet.
        """
        pass

    @abstractmethod
    def static_render(self, **plot_kwargs) -> None:
        """Create a static visualisation of this urban layer.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for rendering the urban layer.

        Args:
            **plot_kwargs: Keyword arguments passed to the underlying plotting function.
                Common parameters include (obviously, this will depend on the implementation):

                - [x] figsize: Tuple specifying figure dimensions
                - [x] column: Column to use for coloring elements
                - [x] cmap: Colormap to use for visualization
                - [x] alpha: Transparency level
                - [x] title: Title for the visualization

        Raises:
            ValueError: If the layer has not been loaded yet.
        """
        pass

    @require_attributes_not_none(
        "layer",
        error_msg="Urban layer not built. Please call from_place() or from_file() first.",
    )
    def map_nearest_layer(
        self,
        data: Union[
            Dict[str, gpd.GeoDataFrame],
            gpd.GeoDataFrame,
        ],
        longitude_column: str | None = None,
        latitude_column: str | None = None,
        output_column: str | None = None,
        threshold_distance: float | None = None,
        **kwargs,
    ) -> Tuple[
        gpd.GeoDataFrame,
        Union[
            Dict[str, gpd.GeoDataFrame],
            gpd.GeoDataFrame,
        ],
    ]:
        """Map points to their nearest elements in this urban layer.

        This method is the public method calling internally the `_map_nearest_layer` method.
        This method performs **spatial joining** of points to their nearest elements in the urban layer.
        It either uses provided column names or processes all mappings defined for this layer.
        This means if `with_mapping(.)` from the `Urban Layer factory` is multiple time called, it'll process the
        spatial join (`_map_narest_layer(.)`) as many times as the mappings has objects.

        Args:
            data: one or more `GeoDataFrame` containing the points to map.
            longitude_column: Name of the column containing longitude values.
                If provided, overrides any predefined mappings.
            latitude_column: Name of the column containing latitude values.
                If provided, overrides any predefined mappings.
            output_column: Name of the column to store the mapping results.
                If provided, overrides any predefined mappings.
            threshold_distance: Maximum distance (in CRS units) to consider for nearest element.
                Points beyond this distance will not be mapped.
            **kwargs: Additional implementation-specific parameters passed to _map_nearest_layer.

        Returns:
            A tuple containing:
            - The updated urban layer `GeoDataFrame` (may be unchanged in some implementations)
            - The input data `GeoDataFrame`(s) with the output column(s) added containing mapping results

        Raises:
            ValueError: If the layer has not been loaded, if required columns are missing,
                if the layer has already been mapped, or if no mappings are defined.

        Examples:
            >>> streets = OSMNXStreets()
            >>> streets.from_place("Manhattan, New York")
            >>> # Using direct column mapping
            >>> _, mapped_data = streets.map_nearest_layer(
            ...     data=taxi_trips,
            ...     longitude_column="pickup_longitude",
            ...     latitude_column="pickup_latitude",
            ...     output_column="nearest_street"
            ... )
            >>> # 👆This essentially adds a new column `nearest_street` to the datataset `taxi_trips` with the nearest street for each of the data-points it is filled-with.
            >>> # Using predefined mappings
            >>> streets = OSMNXStreets()
            >>> streets.from_place("Manhattan, New York")
            >>> streets.mappings = [
            ...     {"longitude_column": "pickup_longitude",
            ...      "latitude_column": "pickup_latitude",
            ...      "output_column": "nearest_pickup_street"}
            ... ] # Much better with the `.with_mapping()` method from the `Urban Layer factory`.
            >>> _, mapped_data = streets.map_nearest_layer(data=taxi_trips)
        """
        if self.has_mapped:
            raise ValueError(
                "This layer has already been mapped. If you want to map again, create a new instance."
            )
        if longitude_column or latitude_column or output_column:
            if not (longitude_column and latitude_column and output_column):
                raise ValueError(
                    "When overriding mappings, longitude_column, latitude_column, and output_column "
                    "must all be specified."
                )
            mapping_kwargs = (
                {"threshold_distance": threshold_distance} if threshold_distance else {}
            )
            mapping_kwargs.update(kwargs)

            if isinstance(data, gpd.GeoDataFrame):
                result = self._map_nearest_layer(
                    data,
                    longitude_column,
                    latitude_column,
                    output_column,
                    **mapping_kwargs,
                )
            else:
                result = {}
                last_key = list(data.keys())[-1]

                for key, gdf in data.items():
                    result[key] = gdf

                    if self.data_id is None or self.data_id == key:
                        self.layer, mapped_data = self._map_nearest_layer(
                            gdf,
                            longitude_column,
                            latitude_column,
                            output_column,
                            _reset_layer_index=key == last_key,
                            **mapping_kwargs,
                        )
                        result[key] = mapped_data

                result = (self.layer, result)

            self.has_mapped = True
            return result

        if not self.mappings:
            raise ValueError(
                "No mappings defined. Use with_mapping() during layer creation."
            )

        mapped_data = data.copy()
        for mapping in self.mappings:
            lon_col = mapping.get("longitude_column", None)
            lat_col = mapping.get("latitude_column", None)
            out_col = mapping.get("output_column", None)
            if not (lon_col and lat_col and out_col):
                raise ValueError(
                    "Each mapping must specify longitude_column, latitude_column, and output_column."
                )

            mapping_kwargs = mapping.get("kwargs", {}).copy()
            if threshold_distance is not None:
                mapping_kwargs["threshold_distance"] = threshold_distance
            mapping_kwargs.update(kwargs)

            if None in [lon_col, lat_col, out_col]:
                raise ValueError(
                    "All of longitude_column, latitude_column, and output_column must be specified."
                )
            if self.mappings[-1]:
                logger.log(
                    "DEBUG_MID",
                    "INFO: Last mapping, resetting urban layer's index.",
                )
            if isinstance(mapped_data, gpd.GeoDataFrame):
                self.layer, temp_mapped = self._map_nearest_layer(
                    mapped_data,
                    lon_col,
                    lat_col,
                    out_col,
                    _reset_layer_index=(mapping == self.mappings[-1]),
                    **mapping_kwargs,
                )
                mapped_data[out_col] = temp_mapped[out_col]
            else:
                temp_mapped_data = {}
                last_key = list(mapped_data.keys())[-1]

                for key, gdf in mapped_data.items():
                    temp_mapped_data[key] = gdf

                    if self.data_id is None or self.data_id == key:
                        self.layer, temp_mapped = self._map_nearest_layer(
                            gdf,
                            lon_col,
                            lat_col,
                            out_col,
                            _reset_layer_index=(
                                mapping == self.mappings[-1] and key == last_key
                            ),
                            **mapping_kwargs,
                        )
                        gdf[out_col] = temp_mapped[out_col]
                        temp_mapped_data[key] = gdf

                mapped_data = temp_mapped_data

        self.has_mapped = True
        return self.layer, mapped_data

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this urban layer.

        Creates a summary or visual representation of the urban layer for quick inspection.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for generating the preview based on the requested format.

            Supported Formats include:

            - [x] ascii: Text-based table format
            - [x] json: JSON-formatted data
            - [ ] html: one may see the HTML representation if necessary in the long term. Open an Issue!
            - [ ] dict: Python dictionary representation if necessary in the long term for re-use in the Python workflow. Open an Issue!
            - [ ] other: Any other formats of interest? Open an Issue!

        Args:
            format: The output format for the preview. Options include:

                - [x] "ascii": Text-based table format
                - [x] "json": JSON-formatted data

        Returns:
            A representation of the urban layer in the requested format.
            Return type varies based on the format parameter.

        Raises:
            ValueError: If the layer has not been loaded yet.
            ValueError: If an unsupported format is requested.
        """
        pass
