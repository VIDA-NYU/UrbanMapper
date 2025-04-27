import geopandas as gpd
from pathlib import Path
from typing import Tuple, Any
from beartype import beartype

from urban_mapper.utils import require_attributes_not_none
from ..abc_urban_layer import UrbanLayerBase


@beartype
class Tile2NetCrosswalks(UrbanLayerBase):
    """Urban layer implementation for crosswalks extracted with `Tile2Net`.

    This class provides access to crosswalk data extracted from aerial imagery using the
    `Tile2Net` deep learning framework. It implements the `UrbanLayerBase` interface, ensuring
    compatibility with other `UrbanMapper` components such as filters, enrichers, and pipelines.

    !!! tip "When to Use?"
        Crosswalk data is particularly useful for:

        - [x] Pedestrian safety analysis
        - [x] Intersection safety studies
        - [x] Accessibility assessment
        - [x] Walkability index calculations
        - [x] Complete streets planning

    Attributes:
        layer (GeoDataFrame): The GeoDataFrame containing crosswalk geometries (set after loading).

    Examples:
        Load and visualise crosswalk data:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> crosswalks = mapper.urban_layer.tile2net_crosswalks().from_file("path/to/crosswalks.geojson")
        >>> crosswalks.static_render(figsize=(10, 8), colour="red")

    !!! note "Data Source"
        Crosswalk data must be pre-extracted using `Tile2Net` and loaded from files. Direct
        loading from place names or other spatial queries is not supported.

        See further here: [Tile2Net VIDA NYU](https://github.com/VIDA-NYU/tile2net) && [This Feature Request](https://github.com/VIDA-NYU/UrbanMapper/issues/17)
    """

    def from_file(self, file_path: str | Path, **kwargs) -> None:
        """Load crosswalk data from a file produced by `Tile2Net`.

        This method reads a spatial data file containing `Tile2Net` output, filters for `crosswalk
        features`, and prepares them for use within the UrbanMapper's workflow

        Args:
            file_path (str | Path): Path to the file containing `Tile2Net` output. Supported formats
                include `GeoJSON`, `Shapefile`, and others compatible with GeoPandas. Note that it needs to be
                exported out of `Tile2Net`. If `Tile2Net` exports is only `Shapefile`, then the file_path
                should point to the `.shp` file, and all other files in the same directory will be loaded.
                If `Tile2Net` supports `GeoJSON` or other `Geopandas` formats at some points, it'll be automatically
                supported here.
            **kwargs: Additional parameters passed to `gpd.read_file()`.

        Returns:
            Self, enabling method chaining.

        Raises:
            ValueError: If the file contains a `feature_id` column, which conflicts with the ID
                column added by this method.
            FileNotFoundError: If the specified file does not exist.

        Examples:
            >>> crosswalks = Tile2NetCrosswalks().from_file("path/to/tile2net_output.geojson")
        """
        self.layer = gpd.read_file(file_path)
        self.layer = self.layer[self.layer["f_type"] == "crosswalk"]
        self.layer = self.layer.to_crs(self.coordinate_reference_system)
        if "feature_id" in self.layer.columns:
            raise ValueError(
                "Feature ID column already exists in the layer. Please remove it before loading."
            )
        self.layer["feature_id"] = self.layer.index

    def from_place(self, place_name: str, **kwargs) -> None:
        """Load crosswalk data for a specific place.

        !!! danger "Not Implemented"
            This method is not yet implemented. Currently, crosswalk data can only be loaded
            from files produced by `Tile2Net`. Future versions may support loading from
            geographic place names or other spatial queries.

            See further in [this feature request](https://github.com/VIDA-NYU/UrbanMapper/issues/17)
        """
        raise NotImplementedError(
            "Loading crosswalks from place is not yet implemented."
        )

    @require_attributes_not_none(
        "layer", error_msg="Layer not loaded. Call from_file() first."
    )
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_crosswalk",
        threshold_distance: float | None = None,
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """Map points to their nearest crosswalk features.

        This internal method identifies the nearest crosswalk for each point in the input
        `GeoDataFrame` and adds a reference to that crosswalk as a new column. It’s primarily
        used by `UrbanLayerBase.map_nearest_layer()` to perform spatial joins between point
        data and crosswalks.

        The method utilises GeoPandas’ spatial join with nearest match to find the closest
        crosswalk for each point. If a threshold distance is specified, points beyond that
        distance will not be matched.

        Args:
            data (GeoDataFrame): GeoDataFrame containing point data to map.
            longitude_column (str): Name of the column containing longitude values.
            latitude_column (str): Name of the column containing latitude values.
            output_column (str): Name of the column to store the indices of nearest crosswalks
                (default: "nearest_crosswalk").
            threshold_distance (float | None): Maximum distance to consider a match, in CRS units
                (default: None).
            _reset_layer_index (bool): Whether to reset the index of the layer GeoDataFrame
                (default: True).
            **kwargs: Additional parameters (not used).

        Returns:
            Tuple[GeoDataFrame, GeoDataFrame]: A tuple containing:
                - The crosswalk network GeoDataFrame (possibly with reset index)
                - The input GeoDataFrame with the new output_column added (filtered if
                  threshold_distance was specified)

        !!! note "Coordinate Reference System"
            The method automatically converts the input data to a projected CRS if it’s not
            already projected, ensuring accurate distance calculations.
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
            layer_projected[["geometry", "feature_id"]],
            how="left",
            max_distance=threshold_distance,
            distance_col="distance_to_crosswalk",
        )
        mapped_data[output_column] = mapped_data["feature_id"]
        return self.layer, mapped_data.drop(
            columns=["feature_id", "distance_to_crosswalk", "index_right"]
        )

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_file() first."
    )
    def get_layer(self) -> gpd.GeoDataFrame:
        """Get the crosswalk network as a GeoDataFrame.

        Returns the crosswalk network as a GeoDataFrame for further analysis or visualisation.

        Returns:
            GeoDataFrame: GeoDataFrame containing the crosswalk segments.

        Raises:
            ValueError: If the layer has not been loaded yet.

        Examples:
            >>> crosswalks = Tile2NetCrosswalks().from_file("path/to/crosswalks.geojson")
            >>> crosswalks_gdf = crosswalks.get_layer()
            >>> print(f"Loaded {len(crosswalks_gdf)} crosswalk segments")
        """
        return self.layer

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_file() first."
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of the crosswalk network.

        Returns the bounding box coordinates of the crosswalk network, useful for spatial
        queries or visualisation extents.

        Returns:
            Tuple[float, float, float, float]: Tuple of (left, bottom, right, top) coordinates
                defining the bounding box.

        Raises:
            ValueError: If the layer has not been loaded yet.

        Examples:
            >>> crosswalks = Tile2NetCrosswalks().from_file("path/to/crosswalks.geojson")
            >>> bbox = crosswalks.get_layer_bounding_box()
            >>> print(f"Crosswalks extent: {bbox}")
        """
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_file() first."
    )
    def static_render(self, **plot_kwargs) -> None:
        """Render the crosswalk network as a static plot.

        Creates a static visualisation of the crosswalk network using GeoPandas’ plotting
        functionality, displayed immediately.

        Args:
            **plot_kwargs: Additional keyword arguments passed to `GeoDataFrame.plot()`.
                Common options include:
                - figsize: Size of the figure as a tuple (width, height)
                - colour: Colour for the crosswalks
                - alpha: Transparency level
                - linewidth: Width of the crosswalk lines
                - edgecolour: Colour for the edges of polygons (if applicable)

        Raises:
            ValueError: If no layer has been loaded yet.

        Examples:
            >>> crosswalks = Tile2NetCrosswalks().from_file("path/to/crosswalks.geojson")
            >>> crosswalks.static_render(figsize=(10, 8), colour="yellow", linewidth=1.5)
        """
        self.layer.plot(**plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this urban layer.

        Produces a textual or structured representation of the `Tile2NetCrosswalks` layer for
        quick inspection, including metadata like the coordinate reference system and mappings.

        Args:
            format (str): Output format for the preview (default: "ascii").
                - "ascii": Text-based format for terminal display
                - "json": JSON-formatted data for programmatic use

        Returns:
            str | dict: A string (for "ascii") or dictionary (for "json") representing the
                crosswalk network layer.

        Raises:
            ValueError: If an unsupported format is requested.

        Examples:
            >>> crosswalks = Tile2NetCrosswalks().from_file("path/to/crosswalks.geojson")
            >>> print(crosswalks.preview())
            >>> # JSON preview
            >>> import json
            >>> print(json.dumps(crosswalks.preview(format="json"), indent=2))
        """
        mappings_str = (
            "\n".join(
                "Mapping:\n"
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
                f"Urban Layer: Tile2NetCrosswalks\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": "Tile2NetCrosswalks",
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
