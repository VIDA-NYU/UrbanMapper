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
    """
    Create a style expression for a given style property based on an attribute.

    :param
        style_property (str): The style property to apply the expression to (e.g., 'stroke-color', 'circle-radius').
        attribute (str): The feature attribute to base the styling on (e.g., 'pickup_count').
        interpolation_type (InterpolationType): The type of interpolation: LINEAR, DISCRETE, or EXACT.
        stops (Union[Dict[Union[float, str], Union[List[float], float]], List[Tuple[Union[float, str], Union[List[float], float]]]]):
            A dictionary or list of tuples mapping attribute values to style values (colors as [r, g, b, a] or numbers).
        default_value (Optional[Union[List[float], float]]): A fallback value if no conditions match (required for DISCRETE and EXACT).

    :example
        >>> # Linear interpolation for 'fill-color'
        >>> stops = {0.0: [0, 255, 255, 1.0], 100.0: [255, 165, 0, 1.0]}
        >>> expr = create_style_expression("fill-color", "count", InterpolationType.LINEAR, stops)
        {'fill-color': ['interpolate', ['linear'], ['get', 'count'], 0.0, [0, 255, 255, 1.0], 100.0, [255, 165, 0, 1.0]]}

        >>> # Discrete interpolation for 'stroke-color'
        >>> stops = [(50.0, [173, 216, 230, 1.0]), (200.0, [255, 255, 0, 1.0])]
        >>> expr = create_style_expression("stroke-color", "value", InterpolationType.DISCRETE, stops, [64, 64, 64, 1.0])
        {'stroke-color': ['case', ['<=', ['get', 'value'], 50.0], [173, 216, 230, 1.0], ['<=', ['get', 'value'], 200.0], [255, 255, 0, 1.0], [64, 64, 64, 1.0]]}

        >>> # Exact matching for 'circle-radius'
        >>> stops = {1.0: 5.0, 2.0: 10.0}
        >>> expr = create_style_expression("circle-radius", "id", InterpolationType.EXACT, stops, 2.0)
        {'circle-radius': ['case', ['==', ['get', 'id'], 1.0], 5.0, ['==', ['get', 'id'], 2.0], 10.0, 2.0]}
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
        self._doc_settings.update(settings)
        return self

    def with_raster_layer(
        self,
        url: str,
        name: str = "Raster Layer",
        attribution: str = "",
        opacity: float = 1.0,
    ) -> "JupyterGisMixin":
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
        if self._doc is None:
            raise ValueError("Document not built. Call build() first.")
        self._doc.save_as(filepath)
