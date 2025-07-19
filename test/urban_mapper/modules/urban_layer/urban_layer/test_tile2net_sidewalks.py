import urban_mapper as um
from urban_mapper.modules import Tile2NetSidewalks
import pytest


# @pytest.mark.skip()
class TestTile2NetSidewalks:
    """
    It tests a Tile2NetSidewalks class.

    """

    layer = Tile2NetSidewalks()
    loader = um.UrbanMapper().loader

    sidewalk_path = "test/data_files/small_NYC-Polygons-09-07-2025_16_09/NYC-Polygons-09-07-2025_16_09.shp"

    file_path = "test/data_files/small_nyc_neighborhoods.csv"
    data_neigborhood_latlong = (
        loader.from_file(file_path)
        .with_columns(latitude_column="latitude", longitude_column="longitude")
        .load()
    )
    data_neigborhood_geom = (
        loader.from_file(file_path).with_columns(geometry_column="geometry").load()
    )

    # #Not suppported
    # def test_from_place(self):
    #   pass

    # #Not suppported
    # def test_from_address(self):
    #   pass

    def test_from_file(self):
        assert self.layer.from_file(self.sidewalk_path) is None

    # #Not suppported
    # def test_from_bbox(self):
    #   pass

    # #Not suppported
    # def test_from_point(self):
    #   pass

    # #Not suppported
    # def test_from_polygon(self):
    #   pass

    # #Not suppported
    # def test_from_xml(self):
    #   pass

    def test_map_nearest_layer(self):
        """
        Lat/Long columns
        """
        if self.layer.layer is None:
            self.layer.from_file(self.sidewalk_path)

        assert (
            self.layer.map_nearest_layer(
                self.data_neigborhood_latlong,
                longitude_column="longitude",
                latitude_column="latitude",
                output_column="sidewalk_near",
            )
            is not None
        )

        """
        Geometry columns
    """
        self.layer = (
            Tile2NetSidewalks()
        )  # It is not possible to map the same layer twice
        self.layer.from_file(self.sidewalk_path)

        assert (
            self.layer.map_nearest_layer(
                self.data_neigborhood_geom,
                geometry_column="geometry",
                output_column="sidewalk_near",
            )
            is not None
        )

        """
        Applying threshold
        It is not possible to map_nearest_layer twice
    """
        self.layer = (
            Tile2NetSidewalks()
        )  # It is not possible to map the same layer twice
        self.layer.from_file(self.sidewalk_path)

        assert (
            self.layer.map_nearest_layer(
                self.data_neigborhood_geom,
                geometry_column="geometry",
                output_column="sidewalk_near",
                threshold_distance=50,
            )
            is not None
        )

    def test_get_layer_bounding_box(self):
        if self.layer.layer is None:
            self.layer.from_file(self.sidewalk_path)

        assert self.layer.get_layer_bounding_box() is not None

    def test_preview(self):
        assert isinstance(self.layer.preview(format="ascii"), str)

        assert isinstance(self.layer.preview(format="json"), dict)

    def test_static_render(self):
        pass
