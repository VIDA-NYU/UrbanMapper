import urban_mapper as um
from urban_mapper.modules import OSMFeatures
import pytest


# @pytest.mark.skip()
class TestImputerFactory:
    """
    It tests a ImputerFactory class.

    """

    loader = um.UrbanMapper().loader
    imputer = um.UrbanMapper().imputer

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

    def test_simple_transform(self):
        """
        Lat/Long columns
        """
        self.imputer.with_type("SimpleGeoImputer").on_columns(
            latitude_column="latitude", longitude_column="longitude"
        )
        assert (
            self.imputer.transform(self.data_neigborhood_latlong, self.layer)
            is not None
        )

        """
        Geometry columns
    """
        self.imputer.with_type("SimpleGeoImputer").on_columns(
            geometry_column="geometry"
        )
        assert (
            self.imputer.transform(self.data_neigborhood_geom, self.layer) is not None
        )

        """
        Many datasets
    """
        data = {
            "neighborhood": self.data_neigborhood_geom,
            "speed_humps": self.data_speed_hump,
        }

        self.imputer.with_type("SimpleGeoImputer").on_columns(
            geometry_column="geometry"
        )
        assert self.imputer.transform(data, self.layer) is not None

        """
        Build method
    """
        imputer = (
            self.imputer.with_type("SimpleGeoImputer")
            .on_columns(geometry_column="geometry")
            .with_data(data_id="neighborhood")
        )
        assert imputer.build() is not None

    def test_address_transform(self):
        """
        Lat/Long columns
        """
        self.imputer.with_type("AddressGeoImputer").on_columns(
            latitude_column="latitude",
            longitude_column="longitude",
            address_column="fake_address",
        )
        assert (
            self.imputer.transform(self.data_neigborhood_latlong, self.layer)
            is not None
        )

        """
        Geometry columns
    """
        self.imputer.with_type("AddressGeoImputer").on_columns(
            geometry_column="geometry", address_column="fake_address"
        )
        assert (
            self.imputer.transform(self.data_neigborhood_geom, self.layer) is not None
        )

        """
        Many datasets but applying to a specific `data_id`
    """
        data = {
            "neighborhood": self.data_neigborhood_geom,
            "speed_humps": self.data_speed_hump,
        }

        self.imputer.with_type("AddressGeoImputer").on_columns(
            geometry_column="geometry", address_column="fake_address"
        ).with_data(data_id="neighborhood")
        assert self.imputer.transform(data, self.layer) is not None

        """
        Build method
    """
        imputer = (
            self.imputer.with_type("AddressGeoImputer")
            .on_columns(geometry_column="geometry", address_column="fake_address")
            .with_data(data_id="neighborhood")
        )
        assert imputer.build() is not None

    def test_preview(self):
        self.imputer.with_type("AddressGeoImputer").on_columns(
            geometry_column="geometry", address_column="fake_address"
        ).with_data(data_id="neighborhood")

        assert self.imputer.preview(format="ascii") is None

        assert self.imputer.preview(format="json") is None
