import json
import os
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple
from jupytergis import GISDocument
from urban_mapper.pipeline import UrbanPipeline


#############################################
#                                           #
#                                           #
#           Will be replace by              #
#     https://arc.net/l/quote/iqsnojyb      #
#                                           #
#                                           #
#############################################
class LayerStyle:
    """Style configuration for map layers in JupyterGIS.

    This class defines how features in a geographic layer should be styled based on
    attribute values. It supports various interpolation types and styling options
    like colour gradients and numeric value ranges.

    Attributes:
        attribute (str): The feature attribute to style based on (e.g., "population", "trip_count").
        stops (Union[Dict[Union[float, str], Union[List[float], float]], List[Tuple[Union[float, str], Union[List[float], float]]]]):
            The mapping of attribute values to style values (colours or numeric values).
            For colours, use [r, g, b, a] format with RGB values in range 0-255 and alpha 0-1.
        interpolation_type (str): The type of interpolation to use:

            - [x] "linear": Smooth transition between values (default)
            - [x] "discrete": Step changes at threshold values
            - [x] "exact": Only exact matches to specific values
        default_value (Optional[Union[List[float], float]]): The fallback value to use when no conditions match.
            Required for "discrete" and "exact" interpolation types.

    Examples:
        >>> # Linear colour gradient based on population
        >>> style = LayerStyle(
        ...     attribute="population",
        ...     stops={0: [240, 240, 240, 1.0], 1000000: [0, 0, 255, 1.0]},
        ...     interpolation_type="linear"
        ... )
        >>>
        >>> # Discrete categories for land use types
        >>> style = LayerStyle(
        ...     attribute="land_use",
        ...     stops={"residential": [255, 0, 0, 1.0], "commercial": [0, 0, 255, 1.0]},
        ...     interpolation_type="exact",
        ...     default_value=[100, 100, 100, 1.0]  # Grey for other categories
        ... )
    """

    def __init__(
        self,
        attribute: str,
        stops: Union[
            Dict[Union[float, str], Union[List[float], float]],
            List[Tuple[Union[float, str], Union[List[float], float]]],
        ],
        interpolation_type: str = "linear",
        default_value: Optional[Union[List[float], float]] = None,
    ):
        self.attribute = attribute
        self.stops = stops
        self.interpolation_type = interpolation_type
        self.default_value = default_value


class InterpolationType(Enum):
    """Enumeration of interpolation types for layer styling.

    Attributes:
        LINEAR (str): Smooth transition between values.
        DISCRETE (str): Step changes at threshold values.
        EXACT (str): Only exact matches to specific values.
    """

    LINEAR = "linear"
    DISCRETE = "discrete"
    EXACT = "exact"


PROPERTY_VALUE_TYPES = {
    "circle-fill-color": "color",
    "fill-color": "color",
    "stroke-color": "color",
    "circle-radius": "number",
    "stroke-width": "number",
}


def create_style_expression(
    style_property: str,
    attribute: str,
    interpolation_type: InterpolationType,
    stops: Union[
        Dict[Union[float, str], Union[List[float], float]],
        List[Tuple[Union[float, str], Union[List[float], float]]],
    ],
    default_value: Optional[Union[List[float], float]] = None,
) -> Dict[str, List]:
    """Create a style expression for a given style property based on an attribute.

    This function generates a style expression that can be used in map layers to
    dynamically style features based on their attribute values. It supports
    different interpolation types to handle how the styling transitions between
    defined stops.

    Args:
        style_property (str): The style property to apply the expression to (e.g., 'stroke-colour', 'circle-radius').
        attribute (str): The feature attribute to base the styling on (e.g., 'pickup_count').
        interpolation_type (InterpolationType): The type of interpolation: LINEAR, DISCRETE, or EXACT.
        stops (Union[Dict[Union[float, str], Union[List[float], float]], List[Tuple[Union[float, str], Union[List[float], float]]]]):
            A dictionary or list of tuples mapping attribute values to style values (colours as [r, g, b, a] or numbers).
        default_value (Optional[Union[List[float], float]], optional): A fallback value if no conditions match (required for DISCRETE and EXACT). Defaults to None.

    Returns:
        Dict[str, List]: A dictionary containing the style expression for the specified property.

    Raises:
        ValueError: If the provided parameters are invalid or incompatible with the interpolation type.

    Examples:
        >>> # Linear interpolation for 'fill-colour'
        >>> stops = {0.0: [0, 255, 255, 1.0], 100.0: [255, 165, 0, 1.0]}
        >>> expr = create_style_expression("fill-colour", "count", InterpolationType.LINEAR, stops)
        >>> # Result: {'fill-colour': ['interpolate', ['linear'], ['get', 'count'], 0.0, [0, 255, 255, 1.0], 100.0, [255, 165, 0, 1.0]]}

        >>> # Discrete interpolation for 'stroke-colour'
        >>> stops = [(50.0, [173, 216, 230, 1.0]), (200.0, [255, 255, 0, 1.0])]
        >>> expr = create_style_expression("stroke-colour", "value", InterpolationType.DISCRETE, stops, [64, 64, 64, 1.0])
        >>> # Result: {'stroke-colour': ['case', ['<=', ['get', 'value'], 50.0], [173, 216, 230, 1.0], ['<=', ['get', 'value'], 200.0], [255, 255, 0, 1.0], [64, 64, 64, 1.0]]}

        >>> # Exact matching for 'circle-radius'
        >>> stops = {1.0: 5.0, 2.0: 10.0}
        >>> expr = create_style_expression("circle-radius", "id", InterpolationType.EXACT, stops, 2.0)
        >>> # Result: {'circle-radius': ['case', ['==', ['get', 'id'], 1.0], 5.0, ['==', ['get', 'id'], 2.0], 10.0, 2.0]}
    """
    value_type = PROPERTY_VALUE_TYPES.get(style_property, "unknown")
    if value_type == "unknown":
        print(
            f"WARNING: Unknown style property '{style_property}'. "
            f"Trusted properties: {list(PROPERTY_VALUE_TYPES.keys())}. "
            "If side effects are observed, ensure using trusted properties."
        )

    if not isinstance(style_property, str) or not style_property.strip():
        raise ValueError("style_property must be a non-empty string.")
    if not isinstance(attribute, str) or not attribute.strip():
        raise ValueError("attribute must be a non-empty string.")
    if not isinstance(interpolation_type, InterpolationType):
        raise ValueError("interpolation_type must be an InterpolationType enum value.")
    if not stops:
        raise ValueError("stops must be non-empty.")

    if isinstance(stops, list):
        stops = dict(stops)
    if not isinstance(stops, dict):
        raise ValueError("stops must be a dictionary or list of tuples.")

    for key, value in stops.items():
        if interpolation_type != InterpolationType.EXACT and not isinstance(
            key, (int, float)
        ):
            raise ValueError(
                f"For {interpolation_type.value} interpolation, stop keys must be numeric; got {key} of type {type(key)}."
            )
        elif interpolation_type == InterpolationType.EXACT and not isinstance(
            key, (int, float, str)
        ):
            raise ValueError(
                f"For exact interpolation, stop keys must be numeric or strings; got {key} of type {type(key)}."
            )

        if value_type == "color":
            if (
                not isinstance(value, list)
                or len(value) != 4
                or not all(isinstance(v, (int, float)) for v in value)
            ):
                raise ValueError(
                    f"For '{style_property}', stop value for {key} must be a list of 4 numbers [r, g, b, a]; got {value}."
                )
            if not all(0 <= v <= 255 for v in value[:3]) or not 0 <= value[3] <= 1:
                raise ValueError(
                    f"Color {value} for {key} must have RGB in [0, 255] and alpha in [0, 1]."
                )
        elif value_type == "number":
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"For '{style_property}', stop value for {key} must be a number; got {value} of type {type(value)}."
                )

    if default_value is not None:
        if value_type == "color":
            if (
                not isinstance(default_value, list)
                or len(default_value) != 4
                or not all(isinstance(v, (int, float)) for v in default_value)
            ):
                raise ValueError(
                    f"For '{style_property}', default_value must be a list of 4 numbers [r, g, b, a]; got {default_value}."
                )
            if (
                not all(0 <= v <= 255 for v in default_value[:3])
                or not 0 <= default_value[3] <= 1
            ):
                raise ValueError(
                    f"Default color {default_value} must have RGB in [0, 255] and alpha in [0, 1]."
                )
        elif value_type == "number":
            if not isinstance(default_value, (int, float)):
                raise ValueError(
                    f"For '{style_property}', default_value must be a number; got {default_value} of type {type(default_value)}."
                )

    expression = []

    if interpolation_type == InterpolationType.LINEAR:
        if len(stops) < 2:
            raise ValueError("Linear interpolation requires at least two stops.")
        expression = ["interpolate", ["linear"], ["get", attribute]]
        for key, value in sorted(stops.items(), key=lambda x: float(x[0])):
            expression.extend([float(key), value])

    elif interpolation_type == InterpolationType.DISCRETE:
        if default_value is None:
            raise ValueError("default_value is required for discrete interpolation.")
        expression = ["case"]
        for key, value in sorted(stops.items(), key=lambda x: float(x[0])):
            expression.extend([["<=", ["get", attribute], float(key)], value])
        expression.append(default_value)

    elif interpolation_type == InterpolationType.EXACT:
        if default_value is None:
            raise ValueError("default_value is required for exact interpolation.")
        expression = ["case"]
        for key, value in stops.items():
            expression.extend([["==", ["get", attribute], key], value])
        expression.append(default_value)

    return {style_property: expression}


##############################################
#                                           #
#                                           #
#                See  above                 #
#     https://arc.net/l/quote/iqsnojyb      #
#                                           #
#                                           #
##############################################


class JupyterGisMixin:
    """Mixin for creating interactive geospatial visualisations using `JupyterGIS` following a `UrbanMapper pipeline`

    This mixin provides a fluent chaining-based methods interface for building interactive maps from
    `UrbanMapper pipeline` results and other geospatial data sources. It integrates
    with the `JupyterGIS library` to create rich, web-based map visualisations
    directly in Jupyter notebooks navigatable together and in real-time.

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>>
        >>> # Initialise UrbanMapper
        >>> mapper = UrbanMapper()
        >>>
        >>> # Have a UrbanPipeline ready in a variable `pipeline`.
        >>>
        >>> # Create a styling configuration
        >>> style = LayerStyle(
        ...     attribute="passenger_count",
        ...     stops={1: [0, 0, 255, 1.0], 4: [255, 0, 0, 1.0]},
        ...     interpolation_type="linear"
        ... )
        >>>
        >>> # Create and display an interactive map
        >>> _, doc = mapper.jupyter_gis.with_pipeline(
        ...     pipeline=pipeline,
        ...     layer_name="Taxi Trips",
        ...     layer_style=style,
        ...     opacity=0.8
        ... ).with_document_settings(
        ...     title="Brooklyn Taxi Trips",
        ...     zoom=12
        ... ).build()
        >>>
        >>> # Display the map
        >>> doc
    """

    def __init__(self) -> None:
        self._pipelines: List[Dict[str, Any]] = []
        self._doc_settings: Dict[str, Any] = {}
        self._layers: List[Dict[str, Any]] = []
        self._filters: List[Dict[str, Any]] = []
        self._doc: Optional[GISDocument] = None

    def with_pipeline(
        self,
        pipeline: Union[str, Any],
        layer_name: str,
        layer_style: LayerStyle,
        opacity: float = 1.0,
        type: Optional[str] = None,
    ):
        """Add an `UrbanMapper pipeline` result as a styled layer on the map.

        This method takes an `UrbanMapper pipeline` and its styling configuration
        and adds the pipeline's urban layer as a layer on the interactive map.

        !!! note "Urban Pipeline as an object, yet also as a file path"
            Note that the pipeline can be passed as an `UrbanPipeline` object or as a file path to a saved / received
            / downloaded pipeline.

        Args:
            pipeline (Union[str, Any]): Either an `UrbanPipeline` object or a file path to a saved pipeline.
            layer_name (str): The name to display for this layer in the map legend.
            layer_style (LayerStyle): A LayerStyle object defining how to style the features based on attributes.
            opacity (float, optional): The opacity of the layer (0.0 to 1.0). Defaults to 1.0.
            type (Optional[str], optional): Override the automatic layer type detection with a specific type
                ("circle", "line", or "fill"). If not provided, the type will be determined based on the geometry type of the features.

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Raises:
            FileNotFoundError: If pipeline is a string path that doesn't exist.
            ValueError: If pipeline is not a valid `UrbanPipeline` or cannot be loaded.

        Examples:
            >>> # Style based on a numeric attribute with colour gradient
            >>> style = LayerStyle(
            ...     attribute="trip_count",
            ...     stops={0: [0, 0, 255, 1.0], 100: [255, 0, 0, 1.0]},
            ...     interpolation_type="linear"
            ... )
            >>>
            >>> # Add the pipeline result as a map layer
            >>> gis_map = mapper.jupyter_gis.with_pipeline(
            ...     pipeline=my_pipeline,
            ...     layer_name="Taxi Trip Destinations",
            ...     layer_style=style,
            ...     opacity=0.7
            ... )
        """
        layer_kwargs = {
            "opacity": opacity,
            "type": type,
        }

        if isinstance(pipeline, str):
            if not os.path.exists(pipeline):
                raise FileNotFoundError(f"Pipeline file not found: {pipeline}")
            try:
                pipeline = UrbanPipeline.load(pipeline)
            except Exception as e:
                raise ValueError(f"Failed to load pipeline from {pipeline}: {e}")

        if not isinstance(pipeline, UrbanPipeline):
            raise ValueError(
                "pipeline must be an UrbanPipeline object or a filepath to a saved pipeline."
            )

        if pipeline.executor._composed:
            urban_layer = pipeline.executor.urban_layer
        else:
            pipeline.compose()
            _, urban_layer = pipeline.transform()

        self._pipelines.append(
            {
                "pipeline": pipeline,
                "layer_name": layer_name,
                "attribute": layer_style.attribute,
                "stops": layer_style.stops,
                "interpolation_type": layer_style.interpolation_type,
                "default_value": layer_style.default_value,
                "layer_kwargs": layer_kwargs,
                "urban_layer": urban_layer,
            }
        )
        return self

    def with_document_settings(self, **settings: Any) -> "JupyterGisMixin":
        """Configure settings for the `JupyterGIS` document.

        This method allows setting various properties of the map document, such as
        `title`, `zoom level`, and `initial extent`.

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            **settings: Keyword arguments for document settings. Common settings include:
                - title (str): The title of the map document.
                - zoom (int): The initial zoom level of the map.
                - extent (List[float]): The initial extent of the map [min_lon, min_lat, max_lon, max_lat].

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Examples:
            >>> gis_map = mapper.jupyter_gis.with_document_settings(
            ...     title="Urban Analysis Map",
            ...     zoom=14,
            ...     extent=[-74.01, 40.71, -73.99, 40.73]
            ... )
        """
        self._doc_settings.update(settings)
        return self

    def with_raster_layer(
        self,
        url: str,
        name: str = "Raster Layer",
        attribution: str = "",
        opacity: float = 1.0,
    ) -> "JupyterGisMixin":
        """Add a raster layer to the map.

        Raster layers are typically used for base maps or background imagery.

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            url (str): The URL of the raster tiles.
            name (str, optional): The name of the layer. Defaults to "Raster Layer".
            attribution (str, optional): Attribution text for the layer. Defaults to "".
            opacity (float, optional): The opacity of the layer (0.0 to 1.0). Defaults to 1.0.

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Examples:
            >>> gis_map = mapper.jupyter_gis.with_raster_layer(
            ...     url="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            ...     name="OpenStreetMap",
            ...     attribution="© OpenStreetMap contributors"
            ... )
        """
        self._layers.append(
            {
                "type": "raster",
                "url": url,
                "name": name,
                "attribution": attribution,
                "opacity": opacity,
            }
        )
        return self

    def with_image_layer(
        self,
        url: str,
        coordinates: List[List[float]],
        name: str = "Image Layer",
        opacity: float = 1.0,
    ) -> "JupyterGisMixin":
        """Add an image layer to the map.

        Image layers are used to display georeferenced images on the map.

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            url (str): The URL of the image.
            coordinates (List[List[float]]): The coordinates defining the image's position.
            name (str, optional): The name of the layer. Defaults to "Image Layer".
            opacity (float, optional): The opacity of the layer (0.0 to 1.0). Defaults to 1.0.

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Examples:
            >>> gis_map = mapper.jupyter_gis.with_image_layer(
            ...     url="path/to/image.png",
            ...     coordinates=[[min_lon, min_lat], [max_lon, max_lat]],
            ...     name="Aerial Imagery"
            ... )
        """
        self._layers.append(
            {
                "type": "image",
                "url": url,
                "coordinates": coordinates,
                "name": name,
                "opacity": opacity,
            }
        )
        return self

    def with_heatmap_layer(
        self,
        feature: str,
        path: Optional[str] = None,
        data: Optional[Dict] = None,
        name: str = "Heatmap Layer",
        opacity: float = 1.0,
        blur: int = 15,
        radius: int = 8,
        gradient: Optional[List[str]] = None,
    ) -> "JupyterGisMixin":
        """Add a heatmap layer to the map.

        Heatmap layers visualise the density of points or other features.

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            feature (str): The feature to visualise in the heatmap.
            path (Optional[str], optional): Path to the data source. Defaults to None.
            data (Optional[Dict], optional): Data for the heatmap. Defaults to None.
            name (str, optional): The name of the layer. Defaults to "Heatmap Layer".
            opacity (float, optional): The opacity of the layer (0.0 to 1.0). Defaults to 1.0.
            blur (int, optional): The blur radius for the heatmap. Defaults to 15.
            radius (int, optional): The radius of influence for each point. Defaults to 8.
            gradient (Optional[List[str]], optional): The colour gradient for the heatmap. Defaults to None.

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Examples:
            >>> gis_map = mapper.jupyter_gis.with_heatmap_layer(
            ...     feature="pickup_locations",
            ...     path="path/to/data.geojson",
            ...     name="Pickup Heatmap",
            ...     blur=10,
            ...     radius=5
            ... )
        """
        self._layers.append(
            {
                "type": "heatmap",
                "feature": feature,
                "path": path,
                "data": data,
                "name": name,
                "opacity": opacity,
                "blur": blur,
                "radius": radius,
                "gradient": gradient,
            }
        )
        return self

    def with_hillshade_layer(
        self,
        url: str,
        name: str = "Hillshade Layer",
        urlParameters: Optional[Dict] = None,
        attribution: str = "",
    ) -> "JupyterGisMixin":
        """Add a hillshade layer to the map.

        Hillshade layers provide a shaded relief effect based on elevation data.

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            url (str): The URL of the hillshade data.
            name (str, optional): The name of the layer. Defaults to "Hillshade Layer".
            urlParameters (Optional[Dict], optional): Additional parameters for the URL. Defaults to None.
            attribution (str, optional): Attribution text for the layer. Defaults to "".

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Examples:
            >>> gis_map = mapper.jupyter_gis.with_hillshade_layer(
            ...     url="path/to/hillshade.tif",
            ...     name="Elevation Hillshade"
            ... )
        """
        self._layers.append(
            {
                "type": "hillshade",
                "url": url,
                "name": name,
                "urlParameters": urlParameters,
                "attribution": attribution,
            }
        )
        return self

    def with_tiff_layer(
        self,
        url: str,
        min: Optional[int] = None,
        max: Optional[int] = None,
        name: str = "Tiff Layer",
        normalize: bool = True,
        wrapX: bool = False,
        attribution: str = "",
        opacity: float = 1.0,
        color_expr: Optional[Any] = None,
    ) -> "JupyterGisMixin":
        """Add a TIFF layer to the map.

        TIFF layers are used for displaying georeferenced raster data.

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            url (str): The URL of the TIFF file.
            min (Optional[int], optional): Minimum value for scaling. Defaults to None.
            max (Optional[int], optional): Maximum value for scaling. Defaults to None.
            name (str, optional): The name of the layer. Defaults to "Tiff Layer".
            normalize (bool, optional): Whether to normalise the data. Defaults to True.
            wrapX (bool, optional): Whether to wrap the X coordinate. Defaults to False.
            attribution (str, optional): Attribution text for the layer. Defaults to "".
            opacity (float, optional): The opacity of the layer (0.0 to 1.0). Defaults to 1.0.
            colour_expr (Optional[Any], optional): Colour expression for styling. Defaults to None.

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Examples:
            >>> gis_map = mapper.jupyter_gis.with_tiff_layer(
            ...     url="path/to/raster.tif",
            ...     name="Elevation Data",
            ...     min=0,
            ...     max=255
            ... )
        """
        self._layers.append(
            {
                "type": "tiff",
                "url": url,
                "min": min,
                "max": max,
                "name": name,
                "normalize": normalize,
                "wrapX": wrapX,
                "attribution": attribution,
                "opacity": opacity,
                "color_expr": color_expr,
            }
        )
        return self

    def with_filter(
        self,
        layer_id: str,
        logical_op: str,
        feature: str,
        operator: str,
        value: Union[str, int, float],
    ) -> "JupyterGisMixin":
        """Add a filter to a layer based on a condition.

        Filters allow you to control which features are displayed on the map based on
        their attributes.

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            layer_id (str): The ID of the layer to apply the filter to.
            logical_op (str): The logical operator to use for combining filters (e.g., "and", "or").
            feature (str): The feature attribute to filter on.
            operator (str): The comparison operator (e.g., "==", ">", "<").
            value (Union[str, int, float]): The value to compare against.

        Returns:
            JupyterGisMixin: The mixin instance for method chaining.

        Examples:
            >>> gis_map = mapper.jupyter_gis.with_filter(
            ...     layer_id="Taxi Trips",
            ...     logical_op="and",
            ...     feature="passenger_count",
            ...     operator=">",
            ...     value=3
            ... )
        """
        self._filters.append(
            {
                "layer_id": layer_id,
                "logical_op": logical_op,
                "feature": feature,
                "operator": operator,
                "value": value,
            }
        )
        return self

    def build(self):
        """Build the interactive map from all configured components.

        This method creates a `JupyterGIS` document from all the configured
        `pipelines`, `layers`, and `settings`, and returns it for display.

        Returns:
            Tuple[JupyterGisMixin, GISDocument]: A tuple containing:

                - [x] The `JupyterGisMixin` instance for method chaining
                - [x] The `GISDocument` object that can be displayed with `doc` at the end of the Jupyter cell.

        Raises:
            ValueError: If a pipeline's geometry type is not supported or if
                the styling configuration is invalid.

        !!! tip "JGIS is a build from scratch type of library"

            - [x] If no base map (raster layer) is added, a default dark basemap will be used
            - [x] If no map extent is specified, it will be calculated automatically from
              the combined bounds of all pipeline layers

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Examples:
            >>> # Build the map after configuring all components
            >>> _, doc = mapper.jupyter_gis\
            ...     .with_pipeline(pipeline=taxi_pipeline, layer_name="Taxi Trips", layer_style=style)\
            ...     .with_document_settings(title="NYC Urban Analysis")\
            ...     .build()
            >>>
            >>> # Display the map in the notebook
            >>> doc
        """
        self._doc = GISDocument(**self._doc_settings)

        if not any(layer["type"] == "raster" for layer in self._layers):
            default_raster = {
                "type": "raster",
                "url": "http://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
                "name": "Default Base Map",
                "attribution": "© OpenStreetMap contributors",
                "opacity": 0.9,
            }
            self._layers.insert(0, default_raster)

        for layer in self._layers:
            if layer["type"] == "raster":
                self._doc.add_raster_layer(
                    url=layer["url"],
                    name=layer["name"],
                    attribution=layer["attribution"],
                    opacity=layer["opacity"],
                )
            elif layer["type"] == "image":
                self._doc.add_image_layer(
                    url=layer["url"],
                    coordinates=layer["coordinates"],
                    name=layer["name"],
                    opacity=layer["opacity"],
                )
            elif layer["type"] == "heatmap":
                self._doc.add_heatmap_layer(
                    feature=layer["feature"],
                    path=layer["path"],
                    data=layer["data"],
                    name=layer["name"],
                    opacity=layer["opacity"],
                    blur=layer["blur"],
                    radius=layer["radius"],
                    gradient=layer["gradient"],
                )
            elif layer["type"] == "hillshade":
                self._doc.add_hillshade_layer(
                    url=layer["url"],
                    name=layer["name"],
                    urlParameters=layer["urlParameters"],
                    attribution=layer["attribution"],
                )
            elif layer["type"] == "tiff":
                self._doc.add_tiff_layer(
                    url=layer["url"],
                    min=layer["min"],
                    max=layer["max"],
                    name=layer["name"],
                    normalize=layer["normalize"],
                    wrapX=layer["wrapX"],
                    attribution=layer["attribution"],
                    opacity=layer["opacity"],
                    color_expr=layer["color_expr"],
                )

        for pipeline_info in self._pipelines:
            urban_layer = pipeline_info["urban_layer"]
            layer_name = pipeline_info["layer_name"]
            attribute = pipeline_info["attribute"]
            stops = pipeline_info["stops"]
            interpolation_type = pipeline_info["interpolation_type"]
            default_value = pipeline_info["default_value"]
            layer_kwargs = pipeline_info["layer_kwargs"]

            layer_type = layer_kwargs.get("type")
            if layer_type is None:
                geometry_type = urban_layer.layer.geometry.geom_type.iloc[0]
                if geometry_type in ["Point", "MultiPoint"]:
                    layer_type = "circle"
                elif geometry_type in ["LineString", "MultiLineString"]:
                    layer_type = "line"
                elif geometry_type in ["Polygon", "MultiPolygon"]:
                    layer_type = "fill"
                else:
                    raise ValueError(f"Unsupported geometry type: {geometry_type}")
                layer_kwargs["type"] = layer_type

            geojson_data = json.loads(urban_layer.layer.to_json())

            style_key = {
                "circle": "circle-fill-color",
                "line": "stroke-color",
                "fill": "fill-color",
            }.get(layer_type)
            if style_key is None:
                raise ValueError(f"Unsupported layer type for styling: {layer_type}")

            try:
                interp_enum = InterpolationType(interpolation_type)
            except ValueError:
                raise ValueError(f"Invalid interpolation_type: {interpolation_type}")

            color_expr = create_style_expression(
                style_property=style_key,
                attribute=attribute,
                interpolation_type=interp_enum,
                stops=stops,
                default_value=default_value,
            )

            self._doc.add_geojson_layer(
                data=geojson_data,
                name=layer_name,
                color_expr=color_expr,
                **layer_kwargs,
            )

        for filter_info in self._filters:
            self._doc.add_filter(**filter_info)

        if "extent" not in self._doc_settings:
            self._doc._options["extent"] = [
                min(
                    pipeline_info["urban_layer"].layer.total_bounds[0]
                    for pipeline_info in self._pipelines
                ),
                min(
                    pipeline_info["urban_layer"].layer.total_bounds[1]
                    for pipeline_info in self._pipelines
                ),
                max(
                    pipeline_info["urban_layer"].layer.total_bounds[2]
                    for pipeline_info in self._pipelines
                ),
                max(
                    pipeline_info["urban_layer"].layer.total_bounds[3]
                    for pipeline_info in self._pipelines
                ),
            ]
        if "latitude" not in self._doc_settings:
            self._doc._options["latitude"] = (
                self._doc._options["extent"][1] + self._doc._options["extent"][3]
            ) / 2

        if "longitude" not in self._doc_settings:
            self._doc._options["longitude"] = (
                self._doc._options["extent"][0] + self._doc._options["extent"][2]
            ) / 2

        return self, self._doc

    def save(self, filepath: str) -> None:
        """Save the interactive map to a JGIS-based file

        !!! note "JGIS Is In Its Early Stages"
            We recommend looking into their documentation in case of something not going as expected.
            If something is outdated, feel free to open an issue on our GitHub repository.

            [JGIS Doc](https://jupytergis.readthedocs.io/en/latest/)

            [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

        Args:
            filepath (str): The path where the JGIS file should be saved.

        Raises:
            ValueError: If build() hasn't been called yet.

        Examples:
            >>> # Build the map and save it to a file
            >>> mapper.jupyter_gis\
            ...     .with_pipeline(pipeline=taxi_pipeline, layer_name="Taxi Trips", layer_style=style)\
            ...     .build()[0]\
            ...     .save("taxi_map.JGIS")
        """
        if self._doc is None:
            raise ValueError("Document not built. Call build() first.")
        self._doc.save_as(filepath)
