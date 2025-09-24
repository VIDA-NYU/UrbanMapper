import pandas as pd
import geopandas as gpd
from urban_mapper import DataFrameLoader
import pytest

# @pytest.mark.skip()
class TestDataFrameLoader:
    file_path = "test/data_files/small_VZV_Speed_Humps_with_LatLon.csv"
    dataframe = pd.read_csv(file_path)

    def test_load(self):
        """
        Lat/Long columns
        """
        loader = DataFrameLoader(
            self.dataframe, longitude_column="longitude", latitude_column="latitude"
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Geometry columns
        """
        loader = DataFrameLoader(self.dataframe, geometry_column="the_geom")
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Source coordinate references
    """
        loader = DataFrameLoader(
            self.dataframe,
            geometry_column="the_geom",
            coordinate_reference_system="EPSG:4326",
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
    """
        loader = DataFrameLoader(
            self.dataframe,
            geometry_column="the_geom",
            coordinate_reference_system=("EPSG:4326", "EPSG:3857"),
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Map column names
    """
        loader = DataFrameLoader(
            self.dataframe,
            geometry_column="the_geom",
            map_columns={"the_geom": "geometry"},
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

    def test_preview(self):
        loader = DataFrameLoader(
            self.dataframe, longitude_column="longitude", latitude_column="latitude"
        )

        assert isinstance(loader.preview(format="ascii"), str)

        assert isinstance(loader.preview(format="json"), dict)
