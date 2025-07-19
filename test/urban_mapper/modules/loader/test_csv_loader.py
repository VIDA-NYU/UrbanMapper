import geopandas as gpd
from urban_mapper import CSVLoader
import pytest


# @pytest.mark.skip()
class TestCSVLoader:
    file_path = "test/data_files/small_VZV_Speed_Humps_with_LatLon.csv"

    def test_load_data_from_file(self):
        """
        Lat/Long columns
        """
        loader = CSVLoader(
            self.file_path, longitude_column="longitude", latitude_column="latitude"
        )
        assert isinstance(loader.load_data_from_file(), gpd.GeoDataFrame)

        """
        Geometry columns
    """
        loader = CSVLoader(self.file_path, geometry_column="the_geom")
        assert isinstance(loader.load_data_from_file(), gpd.GeoDataFrame)

        """
        Source coordinate references
    """
        loader = CSVLoader(
            self.file_path,
            geometry_column="the_geom",
            coordinate_reference_system="EPSG:4326",
        )
        assert isinstance(loader.load_data_from_file(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
    """
        loader = CSVLoader(
            self.file_path,
            geometry_column="the_geom",
            coordinate_reference_system=("EPSG:4326", "EPSG:3857"),
        )
        assert isinstance(loader.load_data_from_file(), gpd.GeoDataFrame)

        """
        Map column names
    """
        loader = CSVLoader(
            self.file_path,
            geometry_column="the_geom",
            map_columns={"the_geom": "geometry"},
        )
        assert isinstance(loader.load_data_from_file(), gpd.GeoDataFrame)

    def test_preview(self):
        loader = CSVLoader(
            self.file_path, longitude_column="longitude", latitude_column="latitude"
        )

        assert isinstance(loader.preview(format="ascii"), str)

        assert isinstance(loader.preview(format="json"), dict)
