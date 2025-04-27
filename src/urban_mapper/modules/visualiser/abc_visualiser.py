from abc import ABC, abstractmethod
from typing import Any, List, Dict
import geopandas as gpd
from urban_mapper.utils.helpers import require_dynamic_columns


class VisualiserBase(ABC):
    """Base class for all visualisers in `UrbanMapper`

    This abstract class defines the common interface that all visualiser implementations
    must follow. Visualisers are responsible for creating visual representations following a `UrbanMapper`'s analysis.

    !!! warning "Method Not Implemented"
        This is an abstract class and cannot be instantiated directly. Use concrete
        implementations such as `StaticVisualiser` or `InteractiveVisualiser` instead.

    Attributes:
        style (Dict[str, Any]): A dictionary of style parameters to apply to the
            visualisation. The specific style parameters depend on the visualiser
            implementation.

    """

    def __init__(self, style: Dict[str, Any] = None):
        self.style = style or {}

    @abstractmethod
    def _render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        """Internal implementation method for rendering visualisations.

        Called by `render()` after validation.

        !!! warning "Method Not Implemented"
            This method must be implemented by subclasses. It should contain the logic
            for creating the visualisation based on the provided GeoDataFrame and columns.

        Args:
            urban_layer_geodataframe (gpd.GeoDataFrame): The `GeoDataFrame` to visualise.
            columns (List[str]): List of column names to include in the visualisation.
            **kwargs: Additional implementation-specific parameters.

        Returns:
            Any: The visualisation result, which varies by implementation.

        Raises:
            ValueError: If the visualisation cannot be performed.
        """
        pass

    @require_dynamic_columns("urban_layer_geodataframe", lambda args: args["columns"])
    def render(
        self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs
    ) -> Any:
        """Render a visualisation of the provided GeoDataFrame

        The primary public method for generating visualisations. It validates inputs and
        delegates to the subclass-specific `_render()` method.

        Args:
            urban_layer_geodataframe (gpd.GeoDataFrame): The `GeoDataFrame` to visualise.
            columns (List[str]): List of column names to include in the visualisation.
                These columns must exist in the `GeoDataFrame`.
            **kwargs: Additional implementation-specific parameters for customising the
                visualisation, such as figure size, title, colours, etc.

        Returns:
            Any: The visualisation result, which varies by implementation (e.g., a plot,
                map, figure, or interactive widget).

        Raises:
            ValueError: If urban_layer_geodataframe lacks a 'geometry' column.
            ValueError: If urban_layer_geodataframe is empty.
            ValueError: If any specified columns don't exist in urban_layer_geodataframe.
            ValueError: If the visualisation cannot be performed.

        Examples:
            >>> from urban_mapper.modules.visualiser import InteractiveVisualiser
            >>> viz = InteractiveVisualiser(style={"color": "red", "opacity": 0.7})
            >>> viz.render(
            ...     urban_layer_geodataframe=enriched_gdf,
            ...     columns=["nearest_street", "distance_to_street"],
            ...     title="Streets Analysis"
            ... )
        """
        if "geometry" not in urban_layer_geodataframe.columns:
            raise ValueError("GeoDataFrame must have a 'geometry' column.")
        if urban_layer_geodataframe.empty:
            raise ValueError("GeoDataFrame is empty; nothing to visualise.")
        return self._render(urban_layer_geodataframe, columns, **kwargs)

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this visualiser.

        Provides a summary of the visualiser's configuration for inspection.

        !!! note "Method Not Implemented"
            This method must be implemented by subclasses. It should return a
            representation of the visualiser's configuration.

        Args:
            format (str): The output format. Options are:

                - [x] "ascii": Text-based format for terminal display.
                - [x] "json": JSON-formatted data for programmatic use.
                Defaults to "ascii".

        Returns:
            Any: A representation of the visualiser in the requested format (e.g., str or dict).

        Raises:
            ValueError: If an unsupported format is specified.

        """
        pass
