from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Dict

import geopandas as gpd
from beartype import beartype
from urban_mapper.utils import require_arguments_not_none
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase


@beartype
class GeoFilterBase(ABC):
    """Base class for all spatial filters in `UrbanMapper`

    This abstract class defines the common interface that all filter implementations
    must follow. Filters are used to subset or filter `GeoDataFrames` based on spatial
    criteria derived from an `urban layer`.

    !!! note
        This is an abstract class and cannot be instantiated directly. Use concrete
        implementations like `BoundingBoxFilter` instead.
    """

    def __init__(
        self,
        data_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.data_id = data_id

    @abstractmethod
    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        """Internal implementation method for filtering a `GeoDataFrame`

        Called by `transform()` after input validation. Subclasses must override this
        method to implement specific filtering logic.

        !!! note "To be implemented by subclasses"
            This method should contain the core logic for filter data given the
            `urban_layer`. It should be implemented in subclasses to handle the
            specific filtering task (e.g., bounding box, polygonal area) and return the
            modified `GeoDataFrame`.

        !!! question "Usefulness of Filters?"
            Filters are essential for narrowing down large datasets to only those
            relevant to a specific analysis or study area. Think of an analysis in
            `Downtown Brooklyn` but your dataset is having data points all over the `New York City & Its Boroughs`.
            In this case, you can use a filter to subset the data to only include points within `Downtown Brooklyn`.

        Args:
            input_geodataframe (gpd.GeoDataFrame): The `GeoDataFrame` to filter.
            urban_layer (UrbanLayerBase): The `urban layer` providing spatial filtering criteria.

        Returns:
            gpd.GeoDataFrame: A filtered `GeoDataFrame` containing only rows meeting the criteria.

        Raises:
            ValueError: If the filtering operation cannot be performed due to invalid inputs.
        """
        ...

    @require_arguments_not_none(
        "input_geodataframe", error_msg="Input GeoDataFrame cannot be None."
    )
    @require_arguments_not_none("urban_layer", error_msg="Urban layer cannot be None.")
    def transform(
        self,
        input_geodataframe: Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame],
        urban_layer: UrbanLayerBase,
    ) -> Union[
        Dict[str, gpd.GeoDataFrame],
        gpd.GeoDataFrame,
    ]:
        """Filter a `GeoDataFrame` based on spatial criteria from an `urban layer`

        The primary public method for applying filters. It validates inputs and delegates
        to the subclass-specific `_transform()` method.

        Args:
            input_geodataframe (Union[Dict[str, GeoDataFrame], GeoDataFrame]): one or more `GeoDataFrame` to filter.
            urban_layer (UrbanLayerBase): The `urban layer` providing spatial filtering criteria.

        Returns:
            Union[Dict[str, GeoDataFrame], GeoDataFrame]: one or more filtered `GeoDataFrame` containing only rows meeting the criteria.

        Raises:
            ValueError: If input_geodataframe or urban_layer is None.
            ValueError: If the filtering operation fails.

        Examples:
            >>> from urban_mapper.modules.filter import BoundingBoxFilter
            >>> from urban_mapper.modules.urban_layer import OSMNXStreets
            >>> streets_layer = OSMNXStreets().from_place("Manhattan, New York")
            >>> bbox_filter = BoundingBoxFilter()
            >>> filtered_data = bbox_filter.transform(taxi_trips, streets_layer)
            >>> filtered_data.head()
            >>> # 👆This would show onloy data within the bounding box of the streets layer. I.e. `Manhattan, New York`.
        """

        if isinstance(input_geodataframe, gpd.GeoDataFrame):
            return self._transform(input_geodataframe, urban_layer)
        else:
            return {
                key: self._transform(gdf, urban_layer)
                if self.data_id is None or self.data_id == key
                else gdf
                for key, gdf in input_geodataframe.items()
            }

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of the filter's configuration.

        Provides a summary of the filter for inspection.

        Args:
            format (str): The output format. Options are:

                - [x] "ascii": Text-based format for terminal display.
                - [x] "json": JSON-formatted data for programmatic use.

                Defaults to "ascii".

        Returns:
            Any: A representation of the filter in the requested format (e.g., str or dict).

        Raises:
            ValueError: If an unsupported format is specified.

        !!! warning "Abstract Method"
            Subclasses must implement this method to provide configuration details.
        """
        pass
