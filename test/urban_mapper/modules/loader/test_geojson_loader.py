import geopandas as gpd
from urban_mapper import GeoJSONLoader
import pytest


# @pytest.mark.skip()
class TestGeoJSONLoader:
    file_path = "test/data_files/small_Street_Construction_Permits_2025.geojson"

    def test_load(self):
        """
        Simple loader
        """
        loader = GeoJSONLoader(
            self.file_path
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Geometry columns and additional columns
        """
        # loader = GeoJSONLoader(self.many_geometry_path, geometry_column="pickup_location", additional_geometry_columns="dropoff_location")
        # assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Source coordinate references
    """
        loader = GeoJSONLoader(
            self.file_path,
            coordinate_reference_system="EPSG:4326",
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
    """
        loader = GeoJSONLoader(
            self.file_path,
            coordinate_reference_system=("EPSG:4326", "EPSG:3857"),
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Map column names
    """
        loader = GeoJSONLoader(
            self.file_path,
            map_columns={"geometry": "the_geometry"},
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

    def test_preview(self):
        loader = GeoJSONLoader(
            self.file_path
        )

        assert isinstance(loader.preview(format="ascii"), str)

        assert isinstance(loader.preview(format="json"), dict)
