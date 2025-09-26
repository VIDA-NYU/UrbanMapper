import urban_mapper as um
from urban_mapper import AddressGeoImputer
from urban_mapper.modules import OSMFeatures
import pytest


# @pytest.mark.skip()
class TestAddressGeoImputer:
    """
    It tests a AddressGeoImputer class.

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
        imputer = AddressGeoImputer(
            latitude_column="latitude",
            longitude_column="longitude",
            address_column="fake_address",
        )
        assert imputer.transform(self.data_neigborhood_latlong, self.layer) is not None

        """
        Geometry columns
    """
        imputer = AddressGeoImputer(
            geometry_column="geometry", address_column="fake_address"
        )
        assert imputer.transform(self.data_neigborhood_geom, self.layer) is not None

        """
        Many datasets but applying to a specific `data_id`
    """
        data_neigborhood = {
            "neighborhood": self.data_neigborhood_geom,
            "speed_humps": self.data_speed_hump,
        }

        imputer = AddressGeoImputer(
            geometry_column="geometry",
            address_column="fake_address",
            data_id="neighborhood",
        )
        assert imputer.transform(data_neigborhood, self.layer) is not None

    def test_preview(self):
        loader = AddressGeoImputer(
            longitude_column="longitude", latitude_column="latitude"
        )

        assert isinstance(loader.preview(format="ascii"), str)

        assert isinstance(loader.preview(format="json"), dict)
