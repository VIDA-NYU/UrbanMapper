import geopandas as gpd
import urban_mapper as um
from urban_mapper import HuggingFaceLoader
import pytest

# @pytest.mark.skip()
class TestHuggingFaceLoader:
    repo_id = "oscur/NYC_speed_humps"
    number_of_rows = 1000

    def test_load(self):
        """
        Lat/Long columns
        """
        loader = HuggingFaceLoader(
            repo_id=self.repo_id, number_of_rows=self.number_of_rows, 
            streaming=False, 
            longitude_column="longitude", 
            latitude_column="latitude"
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Geometry columns
        """
        loader = HuggingFaceLoader(
            repo_id=self.repo_id, number_of_rows=self.number_of_rows, 
            streaming=False, 
            geometry_column="the_geom"
        )        
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Source coordinate references
        """
        loader = HuggingFaceLoader(
            repo_id=self.repo_id, number_of_rows=self.number_of_rows, 
            streaming=False,
            geometry_column="the_geom",
            coordinate_reference_system="EPSG:4326",
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
        """
        loader = HuggingFaceLoader(
            repo_id=self.repo_id, number_of_rows=self.number_of_rows, 
            streaming=False,
            geometry_column="the_geom",
            coordinate_reference_system=("EPSG:4326", "EPSG:3857"),
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Map column names
        """
        loader = HuggingFaceLoader(
            repo_id=self.repo_id, number_of_rows=self.number_of_rows, 
            streaming=False,
            geometry_column="the_geom",
            map_columns={"the_geom": "geometry"},
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)

        """
        Streaming data
        """
        loader = HuggingFaceLoader(
            repo_id=self.repo_id, number_of_rows=self.number_of_rows, 
            streaming=True,
            geometry_column="the_geom"
        )
        assert isinstance(loader.load(), gpd.GeoDataFrame)        

    def test_preview(self):
        loader = HuggingFaceLoader(
            repo_id=self.repo_id, number_of_rows=self.number_of_rows, 
            streaming=False, 
            longitude_column="longitude", 
            latitude_column="latitude"
        )

        assert isinstance(loader.preview(format="ascii"), str)

        assert isinstance(loader.preview(format="json"), dict)
