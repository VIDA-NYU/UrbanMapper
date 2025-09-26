import urban_mapper as um
import pytest


# @pytest.mark.skip()
class TestFilterFactory:
    """
    It tests a FilterFactory class.

    """

    layer = (
        um.UrbanMapper()
        .urban_layer.with_type("streets_intersections")
        .from_place("Brooklyn, New York, USA")
        .build()
    )
    loader = um.UrbanMapper().loader
    filter = um.UrbanMapper().filter

    file_path = "test/data_files/small_nyc_neighborhoods.csv"
    data_neigborhood_latlong = (
        loader.from_file(file_path)
        .with_columns(latitude_column="latitude", longitude_column="longitude")
        .load()
    )
    data_neigborhood_geom = (
        loader.from_file(file_path).with_columns(geometry_column="geometry").load()
    )

    file_path = "test/data_files/small_VZV_Speed_Humps_with_LatLon.csv"
    data_speed_hump = (
        loader.from_file(file_path)
        .with_columns(geometry_column="the_geom")
        .with_map({"the_geom": "geometry"})
        .load()
    )

    def test_transform(self):
        """
        Filtering one dataset with lat/long
        """
        filter = self.filter.with_type("BoundingBoxFilter")
        assert filter.transform(self.data_neigborhood_latlong, self.layer) is not None

        """
        Filtering one dataset with geometry
    """
        filter = self.filter.with_type("BoundingBoxFilter")
        assert filter.transform(self.data_neigborhood_geom, self.layer) is not None

        """
        Filtering many datasets
    """
        data = {
            "neighborhood": self.data_neigborhood_geom,
            "speed_humps": self.data_speed_hump,
        }
        assert filter.transform(data, self.layer) is not None

        """
        Build method
    """
        filter = self.filter.with_type("BoundingBoxFilter")
        assert filter.build() is not None

    def test_preview(self):
        filter = self.filter.with_type("BoundingBoxFilter")

        assert filter.preview(format="ascii") is None

        assert filter.preview(format="json") is None
