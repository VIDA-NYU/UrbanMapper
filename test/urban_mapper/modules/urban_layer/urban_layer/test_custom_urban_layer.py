import urban_mapper as um
from urban_mapper.modules import OSMNXStreets, CustomUrbanLayer
import pytest


# @pytest.mark.skip()
class TestCustomUrbanLayer:
    """
    It tests a CustomUrbanLayer class.

    """

    layer = CustomUrbanLayer()
    loader = um.UrbanMapper().loader

    source_layer = OSMNXStreets()
    source_layer.from_place("Downtown, Brooklyn, New York, USA")

    csv_path = "test/data_files/small_nyc_neighborhoods.csv"
    json_path = "test/data_files/nyc_borough_boundaries.geojson"
    data_neigborhood_latlong = (
        loader.from_file(csv_path)
        .with_columns(latitude_column="latitude", longitude_column="longitude")
        .load()
    )
    data_neigborhood_geom = (
        loader.from_file(csv_path).with_columns(geometry_column="geometry").load()
    )

    # #Not suppported
    #  def test_from_place(self):
    #    pass

    # #Not suppported
    #  def test_from_address(self):
    #    pass

    def test_from_file(self):
        assert self.layer.from_file(self.json_path) is not None

    def test_from_urban_layer(self):
        assert self.layer.from_urban_layer(self.source_layer) is not None

    # #Not suppported
    #  def test_from_bbox(self):
    #    pass

    # #Not suppported
    #  def test_from_point(self):
    #    pass

    # #Not suppported
    #  def test_from_polygon(self):
    #    pass

    # #Not suppported
    #  def test_from_xml(self):
    #    pass

    def test_map_nearest_layer(self):
        """
        Lat/Long columns
        """
        self.layer.from_urban_layer(self.source_layer)
        assert (
            self.layer.map_nearest_layer(
                self.data_neigborhood_latlong,
                longitude_column="longitude",
                latitude_column="latitude",
                output_column="streets_near",
            )
            is not None
        )

        """
        Geometry columns
    """
        self.layer = (
            CustomUrbanLayer()
        )  # It is not possible to map the same layer twice
        self.layer.from_urban_layer(self.source_layer)

        assert (
            self.layer.map_nearest_layer(
                self.data_neigborhood_geom,
                geometry_column="geometry",
                output_column="streets_near",
            )
            is not None
        )

        """
        Applying threshold
    """
        self.layer = (
            CustomUrbanLayer()
        )  # It is not possible to map the same layer twice
        self.layer.from_urban_layer(self.source_layer)

        assert (
            self.layer.map_nearest_layer(
                self.data_neigborhood_geom,
                geometry_column="geometry",
                output_column="streets_near",
                threshold_distance=50,
            )
            is not None
        )

    def test_get_layer_bounding_box(self):
        if self.layer.layer is None:
            self.layer.from_urban_layer(self.source_layer)
            
        assert self.layer.get_layer_bounding_box() is not None

    def test_preview(self):
        assert isinstance(self.layer.preview(format="ascii"), str)

        assert isinstance(self.layer.preview(format="json"), dict)

    def test_static_render(self):
        pass
