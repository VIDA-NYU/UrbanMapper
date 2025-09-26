import urban_mapper as um
import pytest

from urban_mapper.modules.urban_layer import URBAN_LAYER_FACTORY
from shapely import Polygon


# @pytest.mark.skip()
class TestUrbanLayerFactory:
    """
    It tests a UrbanLayerFactory class.

    """

    layer = um.UrbanMapper().urban_layer
    loader = um.UrbanMapper().loader

    csv_path = "test/data_files/small_nyc_neighborhoods.csv"
    json_path = "test/data_files/nyc_borough_boundaries.geojson"
    xml_path = "test/data_files/bryant_park.osm"
    side_crosswalk_path = "test/data_files/small_NYC-Polygons-09-07-2025_16_09/NYC-Polygons-09-07-2025_16_09.shp"
    data_neigborhood_latlong = (
        loader.from_file(csv_path)
        .with_columns(latitude_column="latitude", longitude_column="longitude")
        .load()
    )
    data_neigborhood_geom = (
        loader.from_file(csv_path).with_columns(geometry_column="geometry").load()
    )

    place = "Downtown, Brooklyn, New York, USA"
    address = "370 Jay St, Brooklyn, New York 11201, United States"
    # (left, bottom, right, top)
    bbox = (-74.01, 40.70, -73.97, 40.72)
    # (lat, lon) center point
    point = (40.7536, -73.9832)
    # Bryant Park
    polygon = Polygon(
        [
            [-73.984804, 40.753579],
            [-73.983932, 40.753211],
            [-73.983061, 40.752846],
            [-73.982273, 40.753923],
            [-73.982487, 40.754018],
            [-73.983343, 40.754377],
            [-73.983997, 40.754655],
            [-73.984085, 40.754635],
            [-73.984804, 40.753579],
        ]
    )
    # Brooklyn
    polygon_v2 = Polygon(
        [
            [-74.056688, 40.550339],
            [-73.832945, 40.550339],
            [-73.832945, 40.739434],
            [-74.056688, 40.739434],
            [-74.056688, 40.550339],
        ]
    )

    def test_with_type(self):
        for available_type in URBAN_LAYER_FACTORY:
            assert self.layer.with_type(available_type) is not None

    def test_with_mapping(self):
        for available_type in URBAN_LAYER_FACTORY:
            """
          Lat/Long columns
      """
            assert (
                self.layer.with_type(available_type).with_mapping(
                    longitude_column="longitude",
                    latitude_column="latitude",
                    output_column="mapping_output",
                )
            ) is not None

            """
          Geometry columns
      """
            assert (
                self.layer.with_type(available_type).with_mapping(
                    geometry_column="geometry", output_column="mapping_output"
                )
            ) is not None

            """
          Applying threshold
      """
            assert (
                self.layer.with_type(available_type).with_mapping(
                    geometry_column="geometry",
                    output_column="mapping_output",
                    threshold_distance=50,
                )
            ) is not None

    def test_from_place(self):
        for available_type in URBAN_LAYER_FACTORY:
            if available_type == "streets_features":
                factory = self.layer.with_type(available_type).from_place(
                    self.place, tags={"leisure": ["park", "garden"]}
                )
            elif "region" in available_type:
                factory = self.layer.with_type(available_type).from_place(
                    "New York, New York, USA"
                )
            else:
                factory = self.layer.with_type(available_type).from_place(self.place)

            assert factory is not None

            """
          Build method
      """
            if available_type not in [
                "custom_urban_layer",
                "streets_sidewalks",
                "streets_crosswalks",
            ]:
                assert factory.build() is not None

    def test_from_address(self):
        for available_type in URBAN_LAYER_FACTORY:
            if available_type == "streets_features":
                factory = self.layer.with_type(available_type).from_address(
                    self.address, tags={"building": True}, dist=50.0
                )
            elif "region" in available_type:
                factory = self.layer.with_type(available_type).from_address(
                    "760 United Nations Plaza, Manhattan, New York, United States",
                    dist=100.0,
                )
            else:
                factory = self.layer.with_type(available_type).from_address(
                    self.address, dist=50.0
                )

            assert factory is not None

            """
          Build method
      """
            if available_type not in [
                "custom_urban_layer",
                "streets_sidewalks",
                "streets_crosswalks",
            ]:
                assert factory.build() is not None

    def test_from_bbox(self):
        for available_type in URBAN_LAYER_FACTORY:
            if available_type == "streets_features":
                factory = self.layer.with_type(available_type).from_bbox(
                    self.bbox, tags={"leisure": ["park", "garden"]}
                )
            else:
                factory = self.layer.with_type(available_type).from_bbox(self.bbox)

            assert factory is not None

            """
          Build method
      """
            if available_type not in [
                "custom_urban_layer",
                "streets_sidewalks",
                "streets_crosswalks",
            ]:
                assert factory.build() is not None

    def test_from_point(self):
        for available_type in URBAN_LAYER_FACTORY:
            if available_type == "streets_features":
                factory = self.layer.with_type(available_type).from_point(
                    self.point, tags={"building": True}, dist=50.0
                )
            elif "region" in available_type:
                factory = self.layer.with_type(available_type).from_point(
                    self.point, dist=250.0
                )
            else:
                factory = self.layer.with_type(available_type).from_point(
                    self.point, dist=100.0
                )

            assert factory is not None

            """
          Build method
      """
            if available_type not in [
                "custom_urban_layer",
                "streets_sidewalks",
                "streets_crosswalks",
            ]:
                assert factory.build() is not None

    def test_from_polygon(self):
        for available_type in URBAN_LAYER_FACTORY:
            if available_type == "streets_features":
                factory = self.layer.with_type(available_type).from_polygon(
                    self.polygon, tags={"leisure": ["park", "garden"]}
                )
            elif "region" in available_type:
                factory = self.layer.with_type(available_type).from_polygon(
                    self.polygon_v2
                )
            else:
                factory = self.layer.with_type(available_type).from_polygon(
                    self.polygon
                )

            assert factory is not None

            """
          Build method
      """
            if available_type not in [
                "custom_urban_layer",
                "streets_sidewalks",
                "streets_crosswalks",
            ]:
                assert factory.build() is not None

    def test_from_file(self):
        for available_type in URBAN_LAYER_FACTORY:
            if available_type in ["streets_sidewalks", "streets_crosswalks"]:
                factory = self.layer.with_type(available_type).from_file(
                    self.side_crosswalk_path
                )
            elif "custom_urban_layer" == available_type:
                factory = self.layer.with_type(available_type).from_file(self.json_path)
            else:
                continue

            assert factory is not None

    def test_from_xml(self):
        for available_type in URBAN_LAYER_FACTORY:
            if available_type in ["streets_roads", "streets_intersections"]:
                factory = self.layer.with_type(available_type).from_xml(self.xml_path)
            else:
                continue

            assert factory is not None

    def test_preview(self):
        self.layer.with_type("streets_roads").from_address(
            self.address, dist=50.0
        ).build()

        assert self.layer.preview(format="ascii") is None

        assert self.layer.preview(format="json") is None
