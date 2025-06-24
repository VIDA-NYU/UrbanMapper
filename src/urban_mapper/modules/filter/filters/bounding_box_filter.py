from typing import Any

import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.filter.abc_filter import GeoFilterBase


@beartype
class BoundingBoxFilter(GeoFilterBase):
    """Filter that limits data to the bounding box of an `urban layer`

    Retains only data points or geometries within the `urban layer`’s bounding box,
    using geopandas’ .cx accessor for efficient spatial indexing.

    See further in https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.cx.html

    !!! note
        The bounding box may include areas outside the `urban layer`’s actual features.

    Examples:
        >>> from urban_mapper.modules.filter import BoundingBoxFilter
        >>> from urban_mapper.modules.urban_layer import OSMNXStreets
        >>> streets = OSMNXStreets()
        >>> streets.from_place("Manhattan, New York")
        >>> bbox_filter = BoundingBoxFilter()
        >>> filtered_data = bbox_filter.transform(taxi_trips, streets)
    """

    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        """Filter data to the bounding box of the `urban layer`

        Uses the `urban layer`’s bounding box to filter the input `GeoDataFrame`.

        !!! tip
            Ensure the `urban layer` is fully loaded before applying the filter.

        Args:
            input_geodataframe (gpd.GeoDataFrame): The `GeoDataFrame` to filter.
            urban_layer (UrbanLayerBase): The `urban layer` defining the bounding box.

        Returns:
            gpd.GeoDataFrame: Filtered `GeoDataFrame` within the bounding box.

        Raises:
            AttributeError: If `urban_layer` lacks `get_layer_bounding_box` method.

        """
        if not hasattr(urban_layer, "get_layer_bounding_box"):
            raise AttributeError(
                f"Urban layer {urban_layer.__class__.__name__} does not have a method to get its bounding box."
            )
        minx, miny, maxx, maxy = urban_layer.get_layer_bounding_box()
        return input_geodataframe.cx[minx:maxx, miny:maxy]

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this bounding box filter.

        Provides a summary of the filter’s configuration.

        Args:
            format (str): The output format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            Any: A string (for "ascii") or dict (for "json") representing the filter.

        Raises:
            ValueError: If format is unsupported.

        Examples:
            >>> bbox_filter = BoundingBoxFilter()
            >>> print(bbox_filter.preview())
            Filter: BoundingBoxFilter
              Action: Filter data to the bounding box of the urban layer
        """
        if format == "ascii":
            lines = [
                "Filter: BoundingBoxFilter",
                "  Action: Filter data to the bounding box of the urban layer",
            ]
            if self.data_id:
                lines.append(f"  Data ID: '{self.data_id}'")

            return "\n".join(lines)
        elif format == "json":
            return {
                "filter": "BoundingBoxFilter",
                "action": "Filter data to the bounding box of the urban layer",
                "data_id": self.data_id,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
