from shapely import wkt
from shapely.geometry import base
import pandas as pd
import geopandas as gpd

def validate_wkt_column(dataframe: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Validate WKT strings in a column and filter invalid rows."""
    def is_valid_wkt(wkt_str):
        try:
            geom = wkt.loads(wkt_str)
            return isinstance(geom, base.BaseGeometry)
        except Exception:
            return False

    valid_wkt_mask = dataframe[column_name].apply(is_valid_wkt)
    if not valid_wkt_mask.all():
        dataframe = dataframe[valid_wkt_mask]
    return dataframe

def convert_wkt_to_geometry(dataframe: pd.DataFrame, column_name: str, crs: str) -> gpd.GeoDataFrame:
    """Convert WKT strings in a column to geometries and create a GeoDataFrame."""
    dataframe["geometry"] = dataframe[column_name].apply(wkt.loads)
    geo_dataframe = gpd.GeoDataFrame(dataframe, geometry="geometry", crs=crs)
    geo_dataframe["centroid"] = geo_dataframe["geometry"].centroid
    geo_dataframe["latitude"] = geo_dataframe["centroid"].y
    geo_dataframe["longitude"] = geo_dataframe["centroid"].x
    return geo_dataframe
