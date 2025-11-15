from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from pandas.api.types import is_object_dtype
from thefuzz import process as fuzz_process
from matplotlib import cm as mpl_colormap

from urban_mapper.modules.visualiser.abc_visualiser import VisualiserBase
from lonboard import Map
import ipywidgets as widgets
from IPython.display import display


class LonboardBaseVisualiser(VisualiserBase):
    """Shared Lonboard class to construct Lonboard-based visualisers

    This base class handles the repetitive tasks for all Lonboard-backed
    visualisers, including for instance, map construction, column switching, colourmap
    handling, and CRS validation. Concrete subclasses only need to focus on the
    specifics of how their `lonboard.Map` instance should be created.

    For new Lonboard visualisers, inherit from this class and implement the
    `_create_map` method to build the desired map using the prepared GeoDataFrame
    and resolved style options.

    Attributes:
        allowed_style_keys (ClassVar[set[str]]): Complete list of style keys
            accepted by the visualiser, including passthrough map arguments and
            subclass-specific additions.
        map_passthrough_keys (ClassVar[set[str]]): Keyword arguments that are
            forwarded unchanged to `lonboard.Map`.
        default_map_kwargs (ClassVar[dict[str, Any]]): Default values injected
            into `map_kwargs` when absent.
        allow_polygon_colormap_alias (ClassVar[bool]): Whether the legacy
            `polygon_colormap` alias is accepted.
        colormap_supported_targets (ClassVar[set[str]]): Valid layers that can
            receive colourmap arrays.
        default_colormap_target (ClassVar[str | None]): Fallback target used when
            none is specified.
    """

    allowed_style_keys: ClassVar[Set[str]] = set()
    map_passthrough_keys: ClassVar[Set[str]] = {
        "basemap",
        "controls",
        "custom_attribution",
        "height",
        "parameters",
        "picking_radius",
        "show_side_panel",
        "show_tooltip",
        "use_device_pixels",
        "view",
        "view_state",
    }
    default_map_kwargs: ClassVar[Dict[str, Any]] = {"show_tooltip": True}
    allow_polygon_colormap_alias: ClassVar[bool] = False
    colormap_supported_targets: ClassVar[Set[str]] = set()
    default_colormap_target: ClassVar[Optional[str]] = None

    def _render(
        self,
        urban_layer_geodataframe: gpd.GeoDataFrame,
        columns: List[str],
        **kwargs: Any,
    ) -> Any:
        """Render the Lonboard visualisation

        Normalises and validates the provided GeoDataFrame, resolves any
        supported style options, and prepares data for either direct rendering or
        interactive column switching.

        Args:
            urban_layer_geodataframe (gpd.GeoDataFrame): Source geospatial data to
                visualise.
            columns (List[str]): One or more columns to plot using Lonboard.
            **kwargs: Runtime style overrides merged with the visualiser style.

        Returns:
            Any: Either a `lonboard.Map` instance or an interactive widget that
            allows switching between multiple columns.

        Raises:
            ValueError: If `columns` is empty or contains unknown entries.
            TypeError: If a provided dataframe override is not a GeoDataFrame.
        """
        if not columns:
            raise ValueError("At least one column must be specified.")

        render_options: Dict[str, Any] = {**self.style, **kwargs}
        self._validate_style_options(render_options)

        map_kwargs: Dict[str, Any] = dict(render_options.get("map_kwargs", {}) or {})
        for key in self.map_passthrough_keys:
            if key in render_options:
                map_kwargs.setdefault(key, render_options.pop(key))
        for key, value in self.default_map_kwargs.items():
            map_kwargs.setdefault(key, value)
        render_options["map_kwargs"] = map_kwargs

        data_columns: List[str] = list(dict.fromkeys(columns))
        if "geometry" not in data_columns:
            data_columns.append("geometry")

        base_gdf = urban_layer_geodataframe[data_columns].copy()
        base_gdf = self._ensure_wgs84(base_gdf)
        self._validate_geometries(base_gdf)

        return self._render_column_selection(base_gdf, columns, render_options)

    def _render_column_selection(
        self,
        base_gdf: gpd.GeoDataFrame,
        columns: List[str],
        render_options: Dict[str, Any],
    ) -> Any:
        """Render a selector widget when multiple columns are requested

        Args:
            base_gdf (gpd.GeoDataFrame): Prepared GeoDataFrame containing all
                required columns in WGS84.
            columns (List[str]): Requested columns for visualisation.
            render_options (Dict[str, Any]): Normalised rendering options.

        Returns:
            Any: A `widgets.VBox` containing a dropdown selector and the rendered
            map, or the direct map if only one column is provided.

        Raises:
            ValueError: If none of the requested columns exist in `base_gdf`.
        """
        if len(columns) == 1:
            return self._build_map(base_gdf, columns[0], render_options)

        options = [column for column in columns if column in base_gdf.columns]
        if not options:
            raise ValueError(
                "None of the requested columns were found in the GeoDataFrame."
            )

        dropdown = widgets.Dropdown(
            options=options, value=options[0], description="Column:"
        )
        output = widgets.Output()

        def on_change(change: Dict[str, Any]) -> None:
            if change.get("name") != "value" or change.get("new") is None:
                return
            with output:
                output.clear_output()
                display(self._build_map(base_gdf, change["new"], render_options))

        dropdown.observe(on_change, names="value")

        with output:
            display(self._build_map(base_gdf, options[0], render_options))

        return widgets.VBox([dropdown, output])

    def _build_map(
        self,
        base_gdf: gpd.GeoDataFrame,
        selected_column: str,
        render_options: Dict[str, Any],
    ) -> Map:
        """Create the Lonboard map for a single column

        Args:
            base_gdf (gpd.GeoDataFrame): Base GeoDataFrame prepared for rendering.
            selected_column (str): Column to render on the map.
            render_options (Dict[str, Any]): Validated rendering options.

        Returns:
            lonboard.Map: A configured map instance ready for display.

        Raises:
            ValueError: If `selected_column` is not present in `base_gdf`.
            TypeError: When a dataframe override is provided but is not a
                GeoDataFrame.
        """
        if selected_column not in base_gdf.columns:
            raise ValueError(
                f"Column '{selected_column}' was not found in the GeoDataFrame."
            )

        working_gdf = base_gdf.copy()
        dataframe_override = render_options.get("dataframe")
        prepared_override: Optional[gpd.GeoDataFrame] = None
        if dataframe_override is not None:
            if not isinstance(dataframe_override, gpd.GeoDataFrame):
                raise TypeError("'dataframe' must be provided as a GeoDataFrame.")
            prepared_override = self._prepare_dataframe_for_render(
                self._ensure_wgs84(dataframe_override.copy())
            )

        colormap_source = (
            prepared_override if prepared_override is not None else working_gdf
        )
        colormap_values = self._resolve_colormap(
            colormap_source, selected_column, render_options
        )
        prepared_gdf = self._prepare_dataframe_for_render(working_gdf)
        return self._create_map(
            prepared_gdf,
            selected_column,
            render_options,
            colormap_values,
            prepared_override,
        )

    def _prepare_dataframe_for_render(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Ensure Lonboard-compatible dtypes for non-geometry columns

        Lonboard expects string columns to be explicitly typed. This helper casts
        object columns to string dtype where possible, falling back to `str`
        conversion when a strict cast fails.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame to sanitise prior to rendering.

        Returns:
            gpd.GeoDataFrame: The sanitised GeoDataFrame.
        """
        geometry_column = gdf.geometry.name
        for column_name in gdf.columns:
            if column_name == geometry_column:
                continue
            series = gdf[column_name]
            if is_object_dtype(series):
                try:
                    gdf[column_name] = series.astype("string")
                except (TypeError, ValueError):
                    gdf[column_name] = series.astype(str)
        return gdf

    def _ensure_wgs84(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Convert the GeoDataFrame to WGS84 if required

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame whose CRS should be verified.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame expressed in EPSG:4326.
        """
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            return gdf.to_crs(epsg=4326)
        return gdf

    def _validate_geometries(self, gdf: gpd.GeoDataFrame) -> None:
        """Hook for subclasses to perform geometry validation

        Subclasses can override this method to enforce geometry expectations
        before rendering. The default implementation performs no checks.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame that may be inspected.
        """
        pass

    def _create_map(
        self,
        gdf: gpd.GeoDataFrame,
        selected_column: str,
        render_options: Dict[str, Any],
        colormap_values: Optional[Tuple[str, np.ndarray]],
        data_override: Optional[gpd.GeoDataFrame],
    ) -> Map:
        """Create the Lonboard map for the prepared GeoDataFrame

        Subclasses must implement this method to build their respective
        Lonboard visualisations.

        Args:
            gdf (gpd.GeoDataFrame): Sanitised GeoDataFrame in WGS84.
            selected_column (str): Column currently selected for rendering.
            render_options (Dict[str, Any]): Validated rendering configuration.
            colormap_values (Optional[Tuple[str, np.ndarray]]): Optional target and
                colour array to apply.
            data_override (Optional[gpd.GeoDataFrame]): Optional GeoDataFrame used
                instead of `gdf` when provided.

        Returns:
            Map: The configured Lonboard map instance.
        """
        raise NotImplementedError

    def preview(self, format: str = "ascii") -> Any:
        """Provide a preview of the visualiser configuration

        Args:
            format (str): Output format, either "ascii" or "json".

        Returns:
            Any: A formatted string or dictionary describing the visualiser.

        Raises:
            ValueError: If an unsupported format is requested.
        """
        if format == "ascii":
            style_preview = (
                ", ".join(f"{k}: {v}" for k, v in self.style.items())
                if self.style
                else "Default styling"
            )
            return (
                f"Visualiser: {self.__class__.__name__} using Lonboard\n"
                f"Style: {style_preview}"
            )
        if format == "json":
            return {
                "visualiser": self.__class__.__name__,
                "library": "Lonboard",
                "allowed_style_keys": sorted(self.allowed_style_keys),
                "current_style": self.style,
            }
        raise ValueError(f"Unsupported format '{format}'")

    @classmethod
    def _validate_style_options(cls, options: Dict[str, Any]) -> None:
        """Validate that provided style options are supported.

        Args:
            options (Dict[str, Any]): Style options supplied for rendering.

        Raises:
            ValueError: If unsupported style keys are provided.
        """
        allowed_keys = cls.allowed_style_keys
        invalid_keys = [key for key in options.keys() if key not in allowed_keys]
        if not invalid_keys:
            return

        suggestions: List[str] = []
        for invalid in invalid_keys:
            match = fuzz_process.extractOne(invalid, allowed_keys)
            if match and match[1] >= 90:
                suggestions.append(f"'{invalid}' -> '{match[0]}'")

        suggestion_msg = (
            " Suggestions: " + ", ".join(suggestions) if suggestions else ""
        )
        allowed_formatted = ", ".join(sorted(allowed_keys))
        raise ValueError(
            f"Unsupported style options: {invalid_keys}. Allowed keys: {allowed_formatted}."
            + suggestion_msg
        )

    @classmethod
    def _resolve_colormap(
        cls,
        gdf: gpd.GeoDataFrame,
        selected_column: str,
        render_options: Dict[str, Any],
    ) -> Optional[Tuple[str, np.ndarray]]:
        """Resolve colourmap configuration into Lonboard-ready arrays

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame containing colourmap data.
            selected_column (str): Column being visualised.
            render_options (Dict[str, Any]): Rendering options that may include a `colormap` definition.

        Returns:
            Optional[Tuple[str, np.ndarray]]: Target layer and RGBA array, or `None` if no colourmap is configured.

        Raises:
            ValueError: If the colourmap configuration is invalid for the subclass.
            TypeError: If colourmap options are not provided as a dictionary.
        """
        colormap = render_options.get("colormap")
        polygon_colormap = render_options.get("polygon_colormap")

        if polygon_colormap:
            if not cls.allow_polygon_colormap_alias:
                raise ValueError(
                    "'polygon_colormap' is not supported for this visualiser."
                )
            if colormap:
                raise ValueError(
                    "Provide either 'colormap' or 'polygon_colormap', not both."
                )
            colormap = {**polygon_colormap, "target": "polygon"}

        if not colormap:
            return None

        if not cls.colormap_supported_targets:
            raise ValueError("This visualiser does not support 'colormap'.")

        if not isinstance(colormap, dict):
            raise TypeError("'colormap' must be a dictionary of configuration options.")

        target = colormap.get("target")
        if target is None:
            if cls.default_colormap_target is not None:
                target = cls.default_colormap_target
            elif len(cls.colormap_supported_targets) == 1:
                target = next(iter(cls.colormap_supported_targets))

        if target not in cls.colormap_supported_targets:
            match = fuzz_process.extractOne(target, cls.colormap_supported_targets)
            suggestion = (
                f" Did you mean '{match[0]}'?" if match and match[1] >= 90 else ""
            )
            supported = ", ".join(sorted(cls.colormap_supported_targets))
            raise ValueError(
                f"Unsupported colormap target '{target}'. Supported targets: {supported}."
                + suggestion
            )

        resolved_config = {**colormap}
        resolved_config.setdefault("column", selected_column)
        resolved_config.pop("target", None)
        colour_array = cls._build_numeric_colormap(gdf, resolved_config)
        return target, colour_array

    @staticmethod
    def _build_numeric_colormap(
        gdf: gpd.GeoDataFrame, colormap_options: Dict[str, Any]
    ) -> np.ndarray:
        """Construct an RGBA colourmap array for numeric columns

        Args:
            gdf (gpd.GeoDataFrame): Source GeoDataFrame.
            colormap_options (Dict[str, Any]): Colourmap configuration following
                Matplotlib semantics.

        Returns:
            np.ndarray: Array of RGBA values scaled to `0-255` ready for
            Lonboard consumption.

        Raises:
            ImportError: If Matplotlib is unavailable.
            ValueError: When configuration is incomplete or data cannot be
                converted to numeric values.
            TypeError: If `alpha` is not a numeric scalar.
        """
        column_name = colormap_options.get("column")
        if not column_name:
            raise ValueError(
                "'colormap' requires a 'column' entry specifying the source column."
            )
        if column_name not in gdf.columns:
            raise ValueError(
                f"Column '{column_name}' specified in 'colormap' was not found in the GeoDataFrame."
            )

        raw_series = gdf[column_name]
        numeric_series = pd.to_numeric(raw_series, errors="coerce")
        if numeric_series.isna().all():
            raise ValueError(
                f"Column '{column_name}' could not be converted to numeric values for colour mapping."
            )

        values = numeric_series.to_numpy(dtype=float)
        finite_mask = np.isfinite(values)
        if not finite_mask.any():
            raise ValueError("No finite values available to build the colormap.")

        vmin = colormap_options.get("vmin")
        vmax = colormap_options.get("vmax")
        if vmin is None:
            vmin = float(np.nanmin(values[finite_mask]))
        if vmax is None:
            vmax = float(np.nanmax(values[finite_mask]))
        if not np.isfinite(vmin) or not np.isfinite(vmax):
            raise ValueError("'vmin' and 'vmax' must resolve to finite numeric values.")
        if np.isclose(vmax, vmin):
            normalised = np.zeros_like(values)
        else:
            normalised = (values - vmin) / (vmax - vmin)
        normalised = np.clip(normalised, 0.0, 1.0)

        palette = colormap_options.get("palette", "viridis")
        if isinstance(palette, str):
            cmap = mpl_colormap.get_cmap(palette)
        else:
            cmap = palette
        if colormap_options.get("reverse", False):
            cmap = cmap.reversed()

        rgba = cmap(normalised)

        alpha = colormap_options.get("alpha")
        if alpha is not None:
            if isinstance(alpha, (int, float)):
                scaled_alpha = float(alpha)
                if scaled_alpha > 1:
                    scaled_alpha = scaled_alpha / 255.0
                rgba[..., 3] = np.clip(scaled_alpha, 0.0, 1.0)
            else:
                raise TypeError(
                    "'alpha' must be a numeric scalar between 0-1 or 0-255."
                )

        nan_color = colormap_options.get("nan_color", [0, 0, 0, 0])
        nan_color_arr = np.array(nan_color, dtype=float)
        if nan_color_arr.max() > 1:
            nan_color_arr = nan_color_arr / 255.0
        if nan_color_arr.shape[-1] == 3:
            nan_alpha = colormap_options.get("nan_alpha", 0.0)
            nan_color_arr = np.append(nan_color_arr, nan_alpha)
        rgba[~finite_mask] = nan_color_arr

        rgba = np.nan_to_num(rgba, nan=0.0, copy=False)
        return np.rint(rgba * 255).astype(np.uint8)
