from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import matplotlib.pyplot as plt

import geopandas as gpd
from geopandas import GeoDataFrame
from beartype import beartype
from geopy.exc import GeocoderServiceError, GeocoderUnavailable
from geopy.geocoders import Nominatim
from h3 import cell_area, cell_to_boundary, geo_to_cells, latlng_to_cell
from h3.api.basic_str import LatLngMultiPoly, LatLngPoly
from shapely.geometry import GeometryCollection, MultiPolygon, Point, Polygon, shape
from shapely.ops import unary_union

from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import require_attributes_not_none

from ..abc_urban_layer import UrbanLayerBase


@dataclass(frozen=True)
class _H3GenerationConfig:
    """Configuration describing how a set of H3 cells was generated"""

    resolution: int
    source: str
    metadata: Dict[str, Any]


def _ensure_polygon(
    geometry: Polygon | MultiPolygon | GeometryCollection,
) -> MultiPolygon:
    """Return the geometry as a multipolygon, validating the input"""

    if isinstance(geometry, Polygon):
        if geometry.is_empty:
            raise ValueError("Provided polygon geometry is empty.")
        return MultiPolygon([geometry])
    if isinstance(geometry, MultiPolygon):
        polygons = [poly for poly in geometry.geoms if not poly.is_empty]
        if not polygons:
            raise ValueError("Provided multipolygon contains only empty geometries.")
        return MultiPolygon(polygons)
    if isinstance(geometry, GeometryCollection):
        polygons: List[Polygon] = []
        for geom in geometry.geoms:
            if isinstance(geom, Polygon) and not geom.is_empty:
                polygons.append(geom)
            elif isinstance(geom, MultiPolygon):
                polygons.extend([poly for poly in geom.geoms if not poly.is_empty])
        if not polygons:
            raise ValueError(
                "Geometry collection does not contain any polygonal components."
            )
        return MultiPolygon(polygons)
    raise TypeError(
        "Expected a Polygon, MultiPolygon, or GeometryCollection containing polygons."
    )


def _buffer_in_meters(
    geometry: Polygon | MultiPolygon | Point, distance: float
) -> Polygon | MultiPolygon:
    """Buffer a geometry by a distance in metres (CRS-handled)"""

    if distance <= 0:
        return geometry
    series = gpd.GeoSeries([geometry], crs=DEFAULT_CRS).to_crs("EPSG:3857")
    buffered = series.buffer(distance)
    return buffered.to_crs(DEFAULT_CRS).iloc[0]


def _sorted_cell_ids(cells: Iterable[str]) -> List[str]:
    """Return cell identifiers sorted"""

    return sorted(cells)


def _polygon_to_latlng_poly(polygon: Polygon) -> LatLngPoly:
    """Convert a Shapely polygon into an H3 ``LatLngPoly``"""

    exterior = [(lat, lon) for lon, lat in polygon.exterior.coords]
    holes = [
        [(lat, lon) for lon, lat in interior.coords]
        for interior in polygon.interiors
        if len(interior.coords) >= 3
    ]
    return LatLngPoly(exterior, *holes)


def _geometry_to_h3_shape(geometry: MultiPolygon) -> LatLngPoly | LatLngMultiPoly:
    """Return the appropriate H3 geometry representation for tessellation"""

    latlng_polys = [_polygon_to_latlng_poly(poly) for poly in geometry.geoms if not poly.is_empty]
    if not latlng_polys:
        raise ValueError("Provided geometry does not contain any polygonal area.")
    if len(latlng_polys) == 1:
        return latlng_polys[0]
    return LatLngMultiPoly(*latlng_polys)


def _safe_latlng_to_cell(
    lat: float | None, lon: float | None, resolution: int
) -> str | None:
    """Strict-checked return the H3 cell for coordinates"""

    if lat is None or lon is None:
        return None
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None
    try:
        return latlng_to_cell(lat, lon, resolution)
    except Exception:
        return None


@beartype
class UberH3Grid(UrbanLayerBase):
    """Uber H3 grid urban layer

    Powered by Uber H3 via H3-PY: https://github.com/uber/h3-py/,
    `urbanH3` generates and manages similarly than other urban layers,
    `from_place`, `from_bbox`, etc. methods but by creating instead of
    OSM-based geometries a tessellation of H3 (hexagons) cells given a chosen
    resolution. Each record stores the polygon geometry representing the cell
    boundary together with its identifier and derived metadata such as area in
    square kilometres

    Attributes:
        layer: The GeoDataFrame containing the generated H3 cells.
        resolution: The resolution used to build the layer.
        config: Metadata describing how the current layer was produced.

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> h3_layer = (
        ...     mapper.urban_layer.with_type("uber_h3")
        ...     .from_place("Manhattan, New York City, USA", resolution=9)
        ...     .build()
        ... )
        >>> h3_layer.preview()
    """

    def __init__(self) -> None:
        super().__init__()
        self._geolocator: Optional[Nominatim] = None
        self.config: Optional[_H3GenerationConfig] = None

    def _initialise_layer_frame(
        self, frame: GeoDataFrame, resolution: int
    ) -> GeoDataFrame:
        """Helper to normalise the frame and index rows by the H3 cell identifier

        Args:
            frame: GeoDataFrame containing at least a ``h3_cell_id`` column and geometries representing the corresponding cells.
            resolution: Resolution associated with the provided indexes.

        Returns:
            The processed GeoDataFrame indexed by ``h3_cell_id``.

        Raises:
            ValueError: If the frame does not expose the ``h3_cell_id`` column.
        """

        if "h3_cell_id" not in frame.columns:
            raise ValueError("Layer frame must include an 'h3_cell_id' column.")

        gdf = frame.copy()
        if gdf.crs is None:
            gdf.set_crs(DEFAULT_CRS, inplace=True)
        else:
            gdf = gdf.to_crs(DEFAULT_CRS)

        gdf["h3_cell_id"] = gdf["h3_cell_id"].astype(str)
        gdf["resolution"] = resolution
        if "area_km2" not in gdf.columns:
            gdf["area_km2"] = gdf["h3_cell_id"].apply(
                lambda cell: cell_area(cell, unit="km^2")
            )

        indexed = gdf.set_index("h3_cell_id", drop=False)
        indexed.index.name = None
        self.layer = indexed
        self.resolution = resolution
        return indexed

    def _validate_resolution(self, resolution: int) -> None:
        """API-call to H3 helper to validate a resolution value"""

        if resolution < 0 or resolution > 15:
            raise ValueError("H3 resolution must be between 0 and 15 inclusive.")

    def _build_layer_from_geometry(
        self,
        geometry: Polygon | MultiPolygon | GeometryCollection,
        resolution: int,
        simplify_tolerance: float | None = None,
    ) -> "UberH3Grid":
        """Generate H3 cells covering the provided geometry

        Args:
            geometry: Polygon or multipolygon describing the area of interest.
            resolution: Target H3 resolution.
            simplify_tolerance: Optional tolerance passed to ``simplify`` before
            the H3 tessellation.

        Raises:
            ValueError: If no cells can be generated from the geometry.
        """

        self._validate_resolution(resolution)
        geometry = unary_union(geometry)
        if simplify_tolerance:
            geometry = geometry.simplify(simplify_tolerance)
        multipolygon = _ensure_polygon(geometry)

        cells: set[str] = set()
        h3_geometry = _geometry_to_h3_shape(multipolygon)
        cells.update(geo_to_cells(h3_geometry, resolution))

        if not cells:
            for polygon in multipolygon.geoms:
                if polygon.is_empty:
                    continue
                representative = polygon.representative_point()
                cell = _safe_latlng_to_cell(representative.y, representative.x, resolution)
                if cell:
                    cells.add(cell)

        if not cells:
            raise ValueError("No H3 cells were generated for the provided geometry.")

        cell_ids = _sorted_cell_ids(cells)
        geometries: List[Polygon] = []
        areas_km2: List[float] = []

        for cell_id in cell_ids:
            boundary = cell_to_boundary(cell_id)
            polygon = Polygon([(lng, lat) for lat, lng in boundary])
            geometries.append(polygon)
            areas_km2.append(cell_area(cell_id, unit="km^2"))

        frame = GeoDataFrame(
            {
                "h3_cell_id": cell_ids,
                "resolution": [resolution] * len(cell_ids),
                "area_km2": areas_km2,
            },
            geometry=geometries,
            crs=DEFAULT_CRS,
        )
        self._initialise_layer_frame(frame, resolution)
        return self

    def _get_geolocator(self) -> Nominatim:
        """Lazily initialise and return the Nominatim geolocator instance"""
        if self._geolocator is None:
            self._geolocator = Nominatim(user_agent="urban_mapper_h3")
        return self._geolocator

    def _set_config(self, source: str, resolution: int, **metadata: Any) -> None:
        """Set the internal generation configuration metadata"""

        self.config = _H3GenerationConfig(
            resolution=resolution,
            source=source,
            metadata=metadata,
        )
        self.source = source

    def from_place(
        self,
        place_name: str,
        resolution: int = 9,
        *,
        buffer_meters: float = 0.0,
        simplify_tolerance: float | None = None,
        geocoder_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "UberH3Grid":
        """Build the layer from a place name using Nominatim geocoding

        Args:
            place_name: Human-readable location passed to the geocoder.
            resolution (default: 9): Desired H3 resolution for the generated grid. Note for new users to H3: the higher the resolution, the smaller the cells (max 15).
            buffer_meters: Optional metric buffer applied around the geocoded geometry before tessellation.
            simplify_tolerance: Optional simplification tolerance in degrees via Shapely's ``simplify`` method.
            geocoder_kwargs: Extra keyword arguments forwarded to `Nominatim.geocode`.

        Raises:
            ValueError: If the place cannot be geocoded or no geometry can be
                derived from the response.
        """

        geocoder_kwargs = geocoder_kwargs or {}
        try:
            location = self._get_geolocator().geocode(
                place_name,
                geometry="geojson",
                **geocoder_kwargs,
            )
        except (GeocoderServiceError, GeocoderUnavailable) as exc:
            raise ValueError(f"Geocoding failed for '{place_name}': {exc}") from exc

        if location is None:
            raise ValueError(f"No geocoding result found for '{place_name}'.")

        geometry = None
        raw = getattr(location, "raw", {})
        if "geojson" in raw:
            geometry = shape(raw["geojson"])
            if isinstance(geometry, Point) and "boundingbox" in raw:
                south, north, east, west = map(float, raw["boundingbox"])
                geometry = Polygon(
                    [
                        (west, south),
                        (east, south),
                        (east, north),
                        (west, north),
                        (west, south),
                    ]
                )
        elif "boundingbox" in raw:
            south, north, east, west = map(float, raw["boundingbox"])
            geometry = Polygon(
                [
                    (west, south),
                    (east, south),
                    (east, north),
                    (west, north),
                    (west, south),
                ]
            )
        if geometry is None:
            raise ValueError(
                f"Unable to derive geometry for '{place_name}' from geocoding response."
            )

        if buffer_meters:
            geometry = _buffer_in_meters(geometry, buffer_meters)

        self._set_config(
            source="place",
            resolution=resolution,
            place=place_name,
            buffer_meters=buffer_meters,
        )
        return self._build_layer_from_geometry(
            geometry, resolution, simplify_tolerance=simplify_tolerance
        )

    def from_polygon(
        self,
        polygon: Polygon | MultiPolygon,
        resolution: int = 9,
        *,
        buffer_meters: float = 0.0,
        simplify_tolerance: float | None = None,
        **_: Any,
    ) -> "UberH3Grid":
        """Build the layer from a polygon or multipolygon geometry"""

        geometry: Polygon | MultiPolygon = polygon
        if buffer_meters:
            geometry = _buffer_in_meters(geometry, buffer_meters)

        self._set_config(
            source="polygon",
            resolution=resolution,
            polygon_bounds=list(polygon.bounds),
            polygon_type=polygon.geom_type,
            buffer_meters=buffer_meters,
        )
        return self._build_layer_from_geometry(
            geometry, resolution, simplify_tolerance=simplify_tolerance
        )

    def from_address(
        self,
        address: str,
        dist: float | int,
        resolution: int = 9,
        *,
        simplify_tolerance: float | None = None,
        geocoder_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "UberH3Grid":
        """Build the layer by buffering a geocoded address

        Args:
            address: Address passed to Nominatim.
            dist: Buffer radius in metres.
            resolution (default: 9): Desired H3 resolution. Note for new users to H3: the higher the resolution, the smaller the cells (max 15).
            simplify_tolerance: Optional simplification tolerance in degrees.
            geocoder_kwargs: Additional keyword arguments passed to the geocoder.

        Raises:
            ValueError: If the distance is not positive or the address cannot be
                resolved.
        """

        if dist <= 0:
            raise ValueError("Distance must be a positive number of metres.")
        geocoder_kwargs = geocoder_kwargs or {}
        try:
            location = self._get_geolocator().geocode(address, **geocoder_kwargs)
        except (GeocoderServiceError, GeocoderUnavailable) as exc:
            raise ValueError(f"Geocoding failed for '{address}': {exc}") from exc

        if location is None:
            raise ValueError(f"No geocoding result found for '{address}'.")

        point = Point(location.longitude, location.latitude)
        geometry = _buffer_in_meters(point, dist)

        self._set_config(
            source="address",
            resolution=resolution,
            address=address,
            distance_meters=dist,
        )
        return self._build_layer_from_geometry(
            geometry, resolution, simplify_tolerance=simplify_tolerance
        )

    def from_bbox(
        self,
        bbox: Sequence[float],
        resolution: int = 9,
        *,
        simplify_tolerance: float | None = None,
        **kwargs: Any,
    ) -> "UberH3Grid":
        """Build the layer from a bounding box defined as ``(minx, miny, maxx, maxy)``

        Args:
            bbox: Bounding box coordinates in longitude and latitude order.
            resolution (default: 9): Desired H3 resolution. Note for new users to H3: the higher the resolution, the smaller the cells (max 15).
            simplify_tolerance: Optional simplification tolerance in degrees.
        Raises:
            ValueError: If the bounding box sequence does not contain four values.
        """

        if len(bbox) != 4:
            raise ValueError("Bounding box must be a sequence of four floats.")
        minx, miny, maxx, maxy = map(float, bbox)
        geometry = Polygon(
            [
                (minx, miny),
                (maxx, miny),
                (maxx, maxy),
                (minx, maxy),
                (minx, miny),
            ]
        )
        self._set_config(
            source="bbox",
            resolution=resolution,
            bbox=list(bbox),
        )
        return self._build_layer_from_geometry(
            geometry, resolution, simplify_tolerance=simplify_tolerance
        )

    def from_point(
        self,
        center_point: Tuple[float, float],
        dist: float | int,
        resolution: int = 9,
        *,
        simplify_tolerance: float | None = None,
        **kwargs: Any,
    ) -> "UberH3Grid":
        """Build the layer around a ``(latitude, longitude)`` point buffered by a given distance

        Args:
            center_point: Latitude and longitude of the point to buffer.
            dist: Buffer radius in metres.
            resolution (default: 9): Desired H3 resolution. Note for new users to H3: the higher the resolution, the smaller the cells (max 15).
            simplify_tolerance: Optional simplification tolerance in degrees.

        Raises:
            ValueError: If the distance is not positive.
        """

        if dist <= 0:
            raise ValueError("Distance must be a positive number of metres.")
        latitude, longitude = center_point
        point = Point(longitude, latitude)
        geometry = _buffer_in_meters(point, dist)
        self._set_config(
            source="point",
            resolution=resolution,
            center_point={"lat": latitude, "lon": longitude},
            distance_meters=dist,
        )
        return self._build_layer_from_geometry(
            geometry, resolution, simplify_tolerance=simplify_tolerance
        )

    def from_file(
        self,
        file_path: str | Path,
        **_: Any,
    ) -> "UberH3Grid":
        raise NotImplementedError(
            "UberH3Grid does not support from_file(); use a geospatial builder instead."
        )

    @require_attributes_not_none(
        "layer",
        error_msg="Urban layer not built. Please call a from_* method first.",
    )
    def _map_nearest_layer(
        self,
        data: GeoDataFrame,
        longitude_column: Optional[str] = None,
        latitude_column: Optional[str] = None,
        geometry_column: Optional[str] = None,
        output_column: Optional[str] = "nearest_h3_cell",
        threshold_distance: Optional[float] = None,
        distance_crs: Optional[object] = None,
        _reset_layer_index: Optional[bool] = True,
        **kwargs: object,
    ) -> tuple[GeoDataFrame, GeoDataFrame]:
        """Assign each observation to the containing or nearest H3 cell

        Args:
            data: GeoDataFrame or DataFrame containing the observations.
            longitude_column: Column storing longitude values when
                ``geometry_column`` is not provided.
            latitude_column: Column storing latitude values when
                ``geometry_column`` is not provided.
            geometry_column: Column containing geometries ready for mapping.
            output_column: Name of the column that will receive the mapped H3
                identifier.
            threshold_distance: Optional maximum distance used to filter
                assignments. The units depend on the CRS used for measuring
                distances.
            distance_crs: Optional CRS used when computing distances for the
                ``threshold_distance`` check. When omitted, the current layer
                CRS is used.

        Returns:
            A tuple containing the layer GeoDataFrame and the mapped observations.

        Raises:
            ValueError: If required parameters are missing or the layer has not
                been generated.
        """

        if output_column is None:
            raise ValueError("An output column must be provided for mapping.")
        if self.resolution is None:
            raise ValueError("H3 layer resolution is unknown; build the layer first.")

        points = data.copy()
        if geometry_column:
            if geometry_column not in points.columns:
                raise ValueError(
                    f"Geometry column '{geometry_column}' not found in the data frame."
                )
            points = GeoDataFrame(points, geometry=geometry_column)
        else:
            if longitude_column is None or latitude_column is None:
                raise ValueError(
                    "Longitude and latitude columns must be provided when geometry_column is not set."
                )
            points = GeoDataFrame(
                points,
                geometry=gpd.points_from_xy(
                    points[longitude_column], points[latitude_column]
                ),
            )

        if points.crs is None:
            points.set_crs(DEFAULT_CRS, inplace=True)
        else:
            points = points.to_crs(DEFAULT_CRS)

        layer = self.layer.copy()
        layer_ids = set(layer["h3_cell_id"])

        points[output_column] = [
            _safe_latlng_to_cell(geom.y, geom.x, self.resolution)
            if geom and not geom.is_empty
            else None
            for geom in points.geometry
        ]
        points.loc[~points[output_column].isin(layer_ids), output_column] = None

        if threshold_distance is not None:
            if threshold_distance < 0:
                raise ValueError("threshold_distance must be non-negative.")
            metric_points = (
                points.to_crs(distance_crs) if distance_crs is not None else points
            )
            metric_layer = (
                layer.to_crs(distance_crs) if distance_crs is not None else layer
            )
            polygon_lookup = {
                cell_id: geom
                for cell_id, geom in zip(layer["h3_cell_id"], metric_layer.geometry)
            }
            distances: List[float | None] = []
            for idx, row in metric_points.iterrows():
                cell_id = points.at[idx, output_column]
                if cell_id is None:
                    distances.append(None)
                    continue
                polygon = polygon_lookup.get(cell_id)
                if polygon is None:
                    distances.append(None)
                    continue
                distances.append(polygon.distance(row.geometry))

            mask = [
                dist is not None and dist <= threshold_distance for dist in distances
            ]
            points.loc[[not value for value in mask], output_column] = None

        if _reset_layer_index:
            layer.reset_index(drop=True, inplace=True)
            if "h3_cell_id" in layer.columns:
                layer.set_index("h3_cell_id", drop=False, inplace=True)
                layer.index.name = None

        return layer, points

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not loaded. Call one of the from_* methods first.",
    )
    def get_layer(self) -> GeoDataFrame:
        return self.layer.copy()

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not loaded. Call one of the from_* methods first.",
    )
    def get_layer_bounding_box(self) -> tuple[float, float, float, float]:
        minx, miny, maxx, maxy = self.layer.total_bounds
        return float(minx), float(miny), float(maxx), float(maxy)

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not loaded. Call one of the from_* methods first.",
    )
    def static_render(self, **plot_kwargs: object):
        """Render the H3 layer using GeoPandas plotting

        Args:
            **plot_kwargs: Keyword arguments forwarded to ``GeoDataFrame.plot``.

        Returns:
            Matplotlib axis containing the rendered layer.
        """
        figsize = plot_kwargs.pop("figsize", (10, 8))
        title = None
        if "title" in plot_kwargs:
            title = plot_kwargs.pop("title")
        fig, ax = plt.subplots(figsize=figsize)
        self.layer.plot(ax=ax, **plot_kwargs)
        ax.set_axis_off()
        ax.set_title(title or f"H3 Layer (resolution {self.resolution})")
        return ax

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not loaded. Call one of the from_* methods first.",
    )
    def preview(self, format: str = "ascii") -> str | dict[str, object]:
        """Generate a quick preview of the layer

        Args:
            format: Output format, either "ascii" or "json".

        Returns:
            Either a formatted string or a dictionary summarising the layer.

        Raises:
            ValueError: If the requested format is not supported.
        """

        mappings_str = (
            "\n".join(
                f"    - lon={m.get('longitude_column', 'N/A')}, "
                f"lat={m.get('latitude_column', 'N/A')}, "
                f"geom={m.get('geometry_column', 'N/A')}, "
                f"output={m.get('output_column', 'N/A')}"
                for m in self.mappings
            )
            if self.mappings
            else "    No mappings"
        )

        summary: dict[str, object] = {
            "urban_layer": "UberH3Grid",
            "source": self.config.source if self.config else self.source or "unknown",
            "resolution": self.resolution,
            "cell_count": int(len(self.layer)),
            "total_area_km2": float(self.layer["area_km2"].sum()),
            "mappings": self.mappings,
            "metadata": self.config.metadata if self.config else {},
        }

        if format == "json":
            return summary
        if format == "ascii":
            return (
                "Urban Layer: UberH3Grid\n"
                f"  Source: {summary['source']}\n"
                f"  Resolution: {summary['resolution']}\n"
                f"  Cell count: {summary['cell_count']}\n"
                f"  Total area (km^2): {summary['total_area_km2']:.4f}\n"
                f"  Mappings:\n{mappings_str}"
            )
        raise ValueError(f"Unsupported preview format '{format}'.")
