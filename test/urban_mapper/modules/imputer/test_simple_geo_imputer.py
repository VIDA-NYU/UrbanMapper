import urban_mapper as um
from urban_mapper import SimpleGeoImputer
from urban_mapper.modules import OSMFeatures
import pytest


# @pytest.mark.skip()
class TestSimpleGeoImputer:
    """
    It tests a SimpleGeoImputer class.

    """

    loader = um.UrbanMapper().loader

    file_path = "test/data_files/small_nyc_neighborhoods_missing-values.csv"
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

    ##TODO: Imputers force to pass a `layer` but it's not used.
    layer = OSMFeatures()

    def test_transform(self):
        """
        Lat/Long columns
        """
        imputer = SimpleGeoImputer(
            latitude_column="latitude", longitude_column="longitude"
        )
        assert imputer.transform(self.data_neigborhood_latlong, self.layer) is not None

        """
        Geometry columns
    """
        imputer = SimpleGeoImputer(geometry_column="geometry")
        assert imputer.transform(self.data_neigborhood_geom, self.layer) is not None

        """
        Many datasets
    """
        data_neigborhood = {
            "neighborhood": self.data_neigborhood_geom,
            "speed_humps": self.data_speed_hump,
        }

        assert imputer.transform(data_neigborhood, self.layer) is not None

    def test_preview(self):
        loader = SimpleGeoImputer(
            longitude_column="longitude", latitude_column="latitude"
        )

        assert isinstance(loader.preview(format="ascii"), str)

        assert isinstance(loader.preview(format="json"), dict)
