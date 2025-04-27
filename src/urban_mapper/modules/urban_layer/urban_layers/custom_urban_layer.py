import geopandas as gpd
from pathlib import Path
from typing import Tuple, Any
from beartype import beartype

from urban_mapper.config import DEFAULT_CRS
from ..abc_urban_layer import UrbanLayerBase
from urban_mapper.utils import require_attributes_not_none


@beartype
class CustomUrbanLayer(UrbanLayerBase):
    """`urban_layer` implementation for user-defined spatial layer.

    This class allows users to create `urban layers` from their own spatial information,
    either by loading from files (`shapefiles`, `GeoJSON`) or by using existing
    `urban_layer`s from other libraries, if any. It implements the `UrbanLayerBase interface`, making it compatible
    with other `UrbanMapper` components like `filters`, `enrichers`, and `pipelines`.

    !!! note "Why use CustomUrbanLayer?"
        Custom `urban_layer`s are useful for incorporating domain-specific spatial data
        that may not be available through standard `APIs`, such as:

        - [x] Local government datasets
        - [x] Research-specific spatial information
        - [x] Historical or projected data
        - [x] Specialised analysis results
        - [x] None of the other `urban_layer`s solved your need

    Attributes:
        layer: The `GeoDataFrame` containing the custom spatial data (set after loading).
        source: String indicating how the layer was loaded ("file" or "urban_layer").

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>>
        >>> # Initialise UrbanMapper
        >>> mapper = UrbanMapper()
        >>>
        >>> # Load data from a GeoJSON file
        >>> custom_data = mapper.urban_layer.custom_urban_layer().from_file("path/to/data.geojson")
        >>>
        >>> # Or create from an existing urban layer
        >>> neighborhoods = mapper.urban_layer.region_neighborhoods().from_place("Brooklyn, NY")
        >>> custom_layer = mapper.urban_layer.custom_urban_layer().from_urban_layer(neighborhoods)
    """

    def __init__(self) -> None:
        super().__init__()
        self.source: str | None = None

    def from_file(self, file_path: str | Path, **kwargs) -> "CustomUrbanLayer":
        """Load custom spatial data from a file.

        This method reads spatial data from a `shapefile` (.shp) or `GeoJSON` (.geojson) file
        and prepares it for use as an `urban_layer`. The data is automatically converted
        to the default `coordinate reference system`, i.e `EPSG:4326` (WGS 84),

        Args:
            file_path: Path to the file containing spatial data. Must be a `shapefile`
                or `GeoJSON` file.
            **kwargs: Additional parameters passed to gpd.read_file().

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If the file format is not supported or if the file doesn't
                contain a geometry column.
            FileNotFoundError: If the specified file does not exist.

        Examples:
            >>> custom_layer = CustomUrbanLayer().from_file("path/to/districts.geojson")
            >>> # Visualise the loaded data
            >>> custom_layer.static_render(figsize=(10, 8), column="district_name")
        """
        if not (str(file_path).endswith(".shp") or str(file_path).endswith(".geojson")):
            raise ValueError(
                "Only shapefiles (.shp) and GeoJSON (.geojson) are supported for loading from file."
            )

        self.layer = gpd.read_file(file_path)
        if self.layer.crs is None:
            self.layer.set_crs(DEFAULT_CRS, inplace=True)
        else:
            self.layer = self.layer.to_crs(DEFAULT_CRS)

        if "geometry" not in self.layer.columns:
            raise ValueError("The loaded file does not contain a geometry column.")

        self.source = "file"
        return self

    def from_urban_layer(
        self, urban_layer: UrbanLayerBase, **kwargs
    ) -> "CustomUrbanLayer":
        """Create a custom `urban layer` from an existing `urban layer`.

        This method creates a new custom `urban layer` by copying data from an
        existing `urban_layer`.

        !!! question "Why use this method?"
            This is useful in two scenarios:

            - [x] You do one urban analysis / pipeline workflow. The second one needs to have the results of the previous one (enriched urban layer).
            - [x] For transforming or extending standard `urban_layer`s with custom functionality.

        Args:
            urban_layer: An instance of `UrbanLayerBase` containing the data to copy.
            **kwargs: Additional parameters (not used).

        Returns:
            Self, for method chaining.

        Raises:
            ValueError: If the provided object is not a valid `urban_layer` or
                if the layer has no data.

        Examples:
            >>> # Get neighborhoods from standard layer
            >>> neighborhoods = UrbanMapper().urban_layer.region_neighborhoods().from_place("Chicago")
            >>> # Create custom layer from neighborhoods
            >>> custom = CustomUrbanLayer().from_urban_layer(neighborhoods)
            >>> # Now use custom layer with additional functionality / workflow
        """
        if not isinstance(urban_layer, UrbanLayerBase):
            raise ValueError(
                "The provided object is not an instance of UrbanLayerBase."
            )
        if urban_layer.layer is None:
            raise ValueError(
                "The provided urban layer has no data. Ensure it has been enriched or loaded."
            )

        self.layer = urban_layer.get_layer().copy()
        self.source = "urban_layer"
        return self

    def from_place(self, place_name: str, **kwargs) -> None:
        """Load custom data for a specific place.

        !!! danger "To Not Use – There For Consistency & Compatibility"
            This method is not currently implemented for `CustomUrbanLayer`, as custom
            layers require data to be loaded explicitly from files or other `urban_layer`s
            rather than from geocoded place names.
        """
        raise NotImplementedError(
            "Loading from place is not supported for CustomUrbanLayer."
        )

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not loaded. Call from_file() or from_urban_layer() first.",
    )
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_feature",
        threshold_distance: float | None = None,
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """Map points to their `nearest features` in the `custom layer`.

        This internal method finds the `nearest feature` in the `custom layer` for each point
        in the input `GeoDataFrame` and adds a reference to that feature as a new column.

        It's primarily used by the `UrbanLayerBase.map_nearest_layer()` method to
        implement spatial joining between your dataset point data and custom urban layer's components.

        The method uses `GeoPandas`' spatial join with nearest match to find the
        closest feature for each point. If a threshold distance is specified,
        points beyond that distance will not be matched.

        Args:
            data: `GeoDataFrame` containing point data to map.
            longitude_column: Name of the column containing longitude values.
            latitude_column: Name of the column containing latitude values.
            output_column: Name of the column to store the indices of nearest features.
            threshold_distance: Maximum distance to consider a match, in the CRS units.
            _reset_layer_index: Whether to reset the index of the layer `GeoDataFrame`.
            **kwargs: Additional parameters (not used).

        Returns:
            A tuple containing:
                - The custom layer `GeoDataFrame` (possibly with reset index)
                - The input `GeoDataFrame` with the new output_column added
                  (filtered if threshold_distance was specified)

        !!! note "To Keep In Mind"

            - [x] The method automatically converts the input data to a projected CRS if
              it's not already projected, which is necessary for accurate distance
              calculations.
            - [x] Any duplicate indices in the result are removed to ensure a clean result.
        """
        dataframe = data.copy()

        if "geometry" not in dataframe.columns:
            dataframe = gpd.GeoDataFrame(
                dataframe,
                geometry=gpd.points_from_xy(
                    dataframe[longitude_column], dataframe[latitude_column]
                ),
                crs=self.coordinate_reference_system,
            )

        if not dataframe.crs.is_projected:
            utm_crs = dataframe.estimate_utm_crs()
            dataframe = dataframe.to_crs(utm_crs)
            layer_projected = self.layer.to_crs(utm_crs)
        else:
            layer_projected = self.layer

        mapped_data = gpd.sjoin_nearest(
            dataframe,
            layer_projected[["geometry"]],
            how="left",
            max_distance=threshold_distance,
            distance_col="distance_to_feature",
        )
        mapped_data[output_column] = mapped_data.index_right

        if mapped_data.index.duplicated().any():
            mapped_data = mapped_data.reset_index(drop=True)

        if _reset_layer_index:
            self.layer = self.layer.reset_index()

        return self.layer, mapped_data.drop(
            columns=["distance_to_feature", "index_right"], errors="ignore"
        )

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call from_file() or from_urban_layer() first.",
    )
    def get_layer(self) -> gpd.GeoDataFrame:
        """Get the custom layer as a `GeoDataFrame`.

        This method returns the custom layer as a `GeoDataFrame`, which can be
        used for further analysis or visualisation purposes.

        Returns:
            `GeoDataFrame` containing the custom layer data.

        Raises:
            ValueError: If the layer has not been loaded yet.

        Examples:
            >>> custom_layer = CustomUrbanLayer().from_file("path/to/data.geojson")
            >>> custom_gdf = custom_layer.get_layer()
            >>> # Analyse the data
            >>> print(f"Layer has {len(custom_gdf)} features")
        """
        return self.layer

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call from_file() or from_urban_layer() first.",
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get the `bounding box` of the `custom layer`.

        This method returns the `bounding box` coordinates of the `custom layer`,
        which can be used for spatial queries, visualisation extents, or other
        geospatial operations.

        Returns:
            Tuple of (`left`, `bottom`, `right`, `top`) coordinates defining the bounding box.

        Raises:
            ValueError: If the layer has not been loaded yet.

        Examples:
            >>> custom_layer = CustomUrbanLayer().from_file("path/to/data.geojson")
            >>> bbox = custom_layer.get_layer_bounding_box()
            >>> print(f"Layer covers area: {bbox}")
        """
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call from_file() or from_urban_layer() first.",
    )
    def static_render(self, **plot_kwargs) -> None:
        """Render the `custom layer` as a `static plot`.

        This method creates a static visualisation of the custom layer using
        `GeoPandas`' plotting functionality. The plot is displayed immediately.

        Args:
            **plot_kwargs: Additional keyword arguments to pass to GeoDataFrame.plot().
                Common options include:

                - [x] figsize: Size of the figure as a tuple (width, height)
                - [x] column: Name of the column to use for coloring features
                - [x] cmap: Colormap to use for visualisation
                - [x] alpha: Transparency level
                - [x] edgecolor: Color for the edges of polygons

        Raises:
            ValueError: If no layer has been loaded yet.

        Examples:
            >>> custom_layer = CustomUrbanLayer().from_file("path/to/districts.geojson")
            >>> # Create a choropleth map by population
            >>> custom_layer.static_render(
            ...     figsize=(10, 8),
            ...     column="population",
            ...     cmap="viridis",
            ...     legend=True
            ... )
        """
        self.layer.plot(**plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this `urban_layer`.

        This method creates a textual or structured representation of the `CustomUrbanLayer`
        for quick inspection. It includes metadata about the layer such as its `source`,
        `coordinate reference system`, and `any mappings` that have been defined.

        Args:
            format: The output format for the preview (default: "ascii").

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use

        Returns:
            A string (for `ASCII` format) or dictionary (for `JSON` format) representing
            the `custom layer`.

        Raises:
            ValueError: If an unsupported format is requested.

        Examples:
            >>> custom_layer = CustomUrbanLayer().from_file("path/to/data.geojson")
            >>> # ASCII preview
            >>> print(custom_layer.preview())
            >>> # JSON preview
            >>> import json
            >>> print(json.dumps(custom_layer.preview(format="json"), indent=2))
        """
        mappings_str = (
            "\n".join(
                f"    - lon={m.get('longitude_column', 'N/A')}, "
                f"lat={m.get('latitude_column', 'N/A')}, "
                f"output={m.get('output_column', 'N/A')}"
                for m in self.mappings
            )
            if self.mappings
            else "    No mappings"
        )
        if format == "ascii":
            return (
                f"Urban Layer: CustomUrbanLayer\n"
                f"  Source: {self.source or 'Not loaded'}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": "CustomUrbanLayer",
                "source": self.source or "Not loaded",
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
