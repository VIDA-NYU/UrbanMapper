import pandas as pd
import geopandas as gpd
from shapely.geometry import (
    Point,
    LineString,
    Polygon,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
)


def extract_point_coord(geoseries: gpd.GeoSeries) -> pd.DataFrame:
    """Extracts a list of points from many different geometry objects

    Args:
        geoseries: Series with geometry in a WKT format

    Returns:
        A dataframe with points `x` and `y` (longitude, latitude) and row index.
    """
    indices = []
    points = []

    for idx, geometry in geoseries.items():
        if isinstance(geometry, (Polygon, LineString)):
            coordinates = geometry.exterior.coords if isinstance(geometry, Polygon) else geometry.coords
            coordinates = [list(point) for point in coordinates]
        elif isinstance(geometry, (MultiPolygon, MultiLineString)):
            coordinates = [
                list(point)
                for sub_geometry in geometry.geoms
                for point in (sub_geometry.exterior.coords if isinstance(sub_geometry, Polygon) else sub_geometry.coords)
            ]
        elif isinstance(geometry, MultiPoint):
            coordinates = [[sub_point.x, sub_point.y] for sub_point in geometry.geoms]
        elif isinstance(geometry, Point):
            coordinates = [[geometry.x, geometry.y]]

        indices.extend([idx] * len(coordinates))
        points.extend(coordinates)

    return pd.DataFrame(points, columns=["x", "y"], index=indices)
