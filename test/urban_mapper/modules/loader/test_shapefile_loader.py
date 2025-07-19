import geopandas as gpd
from urban_mapper import ShapefileLoader
import pytest


# @pytest.mark.skip()
class TestShapefileLoader:
    file_path = "test/data_files/small_PLUTO/MapPLUTO_UNCLIPPED.shp"

    def test_load_data_from_file(self):
        """
        Source coordinate references
        """
        loader = ShapefileLoader(
            self.file_path, coordinate_reference_system="EPSG:4326"
        )
        assert isinstance(loader.load_data_from_file(), gpd.GeoDataFrame)

        """
        Map column names
    """
        loader = ShapefileLoader(self.file_path, map_columns={"Shape_Area": "area"})
        assert isinstance(loader.load_data_from_file(), gpd.GeoDataFrame)

    def test_preview(self):
        loader = ShapefileLoader(self.file_path)

        assert isinstance(loader.preview(format="ascii"), str)

        assert isinstance(loader.preview(format="json"), dict)
