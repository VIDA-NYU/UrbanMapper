import geopandas as gpd, pandas as pd
import urban_mapper as um
import pytest


# @pytest.mark.skip()
class TestLoaderFactory:
    loader = um.UrbanMapper().loader

    csv_path = "test/data_files/small_VZV_Speed_Humps_with_LatLon.csv"
    parquet_path = "test/data_files/small_VZV_Speed_Humps_with_LatLon.parquet"
    shape_path = "test/data_files/small_PLUTO/MapPLUTO_UNCLIPPED.shp"
    hugginface_path = "oscur/NYC_speed_humps"
    number_of_rows = 1000

    def test_with_columns_called_twice_raises_value_error(self):
        loader_factory = self.loader.from_file(self.csv_path).with_columns(
            longitude_column="longitude", latitude_column="latitude"
        )

        with pytest.raises(ValueError, match="with_columns has already been configured"):
            loader_factory.with_columns(geometry_column="the_geom")

    def test_from_csv_file(self):
        """
        Lat/Long columns
        """
        data = self.loader.from_file(self.csv_path).with_columns(
            longitude_column="longitude", latitude_column="latitude"
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Geometry columns
    """
        data = self.loader.from_file(self.csv_path).with_columns(
            geometry_column="the_geom"
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source coordinate references
    """
        data = (
            self.loader.from_file(self.csv_path)
            .with_columns(geometry_column="the_geom")
            .with_crs("EPSG:4326")
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
    """
        data = (
            self.loader.from_file(self.csv_path)
            .with_columns(geometry_column="the_geom")
            .with_crs(("EPSG:4326", "EPSG:2263"))
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Map column names
    """
        data = (
            self.loader.from_file(self.csv_path)
            .with_columns(geometry_column="the_geom")
            .with_map({"Shape_STLe": "shape"})
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Build method
    """
        loader = (
            self.loader.from_file(self.csv_path)
            .with_columns(geometry_column="the_geom")
            .with_crs(("EPSG:4326", "EPSG:2263"))
            .with_map({"Shape_STLe": "shape"})
        )
        assert loader.build() is not None

    def test_from_parquet_file(self):
        """
        Lat/Long columns
        """
        data = self.loader.from_file(self.parquet_path).with_columns(
            longitude_column="longitude", latitude_column="latitude"
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Geometry columns
    """
        data = self.loader.from_file(self.parquet_path).with_columns(
            geometry_column="the_geom"
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source coordinate references
    """
        data = (
            self.loader.from_file(self.parquet_path)
            .with_columns(geometry_column="the_geom")
            .with_crs("EPSG:4326")
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
    """
        data = (
            self.loader.from_file(self.parquet_path)
            .with_columns(geometry_column="the_geom")
            .with_crs(("EPSG:4326", "EPSG:2263"))
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Map column names
    """
        data = (
            self.loader.from_file(self.parquet_path)
            .with_columns(geometry_column="the_geom")
            .with_map({"Shape_STLe": "shape"})
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Build method
    """
        loader = (
            self.loader.from_file(self.parquet_path)
            .with_columns(geometry_column="the_geom")
            .with_crs(("EPSG:4326", "EPSG:2263"))
            .with_map({"Shape_STLe": "shape"})
        )
        assert loader.build() is not None

    # TODO: Why does shape file require with_columns?
    def test_from_shape_file(self):
        """
        Source-target coordinate references
        """
        data = (
            self.loader.from_file(self.shape_path)
            .with_columns(geometry_column="geometry")
            .with_crs(("EPSG:4326", "EPSG:4326"))
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Map column names
    """
        data = (
            self.loader.from_file(self.shape_path)
            .with_columns(geometry_column="geometry")
            .with_map({"Shape_Area": "area"})
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Build method
    """
        loader = (
            self.loader.from_file(self.shape_path)
            .with_columns(geometry_column="geometry")
            .with_crs(("EPSG:4326", "EPSG:4326"))
            .with_map({"Shape_Area": "area"})
        )
        assert loader.build() is not None

    def test_from_dataframe(self):
        dataframe = pd.read_csv(self.csv_path)

        """
        Lat/Long columns
    """
        data = self.loader.from_dataframe(dataframe).with_columns(
            longitude_column="longitude", latitude_column="latitude"
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Geometry columns
    """
        data = self.loader.from_dataframe(dataframe).with_columns(
            geometry_column="the_geom"
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source coordinate references
    """
        data = (
            self.loader.from_dataframe(dataframe)
            .with_columns(geometry_column="the_geom")
            .with_crs("EPSG:4326")
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
    """
        data = (
            self.loader.from_dataframe(dataframe)
            .with_columns(geometry_column="the_geom")
            .with_crs(("EPSG:4326", "EPSG:2263"))
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Map column names
    """
        data = (
            self.loader.from_dataframe(dataframe)
            .with_columns(geometry_column="the_geom")
            .with_map({"Shape_STLe": "shape"})
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Build method
    """
        loader = self.loader.from_dataframe(dataframe).with_columns(geometry_column="the_geom").with_crs(("EPSG:4326", "EPSG:2263")).with_map({"Shape_STLe": "shape"})
        assert loader.build() is not None

    def test_from_huggingface(self):
        """
        Lat/Long columns
        """
        data = self.loader.from_huggingface(self.hugginface_path, number_of_rows=self.number_of_rows).with_columns(
            longitude_column="longitude", latitude_column="latitude", 
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Geometry columns
    """
        data = self.loader.from_huggingface(self.hugginface_path, number_of_rows=self.number_of_rows).with_columns(
            geometry_column="the_geom"
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source coordinate references
    """
        data = (
            self.loader.from_huggingface(self.hugginface_path, number_of_rows=self.number_of_rows)
            .with_columns(geometry_column="the_geom")
            .with_crs("EPSG:4326")
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Source-target coordinate references
    """
        data = (
            self.loader.from_huggingface(self.hugginface_path, number_of_rows=self.number_of_rows)
            .with_columns(geometry_column="the_geom")
            .with_crs(("EPSG:4326", "EPSG:2263"))
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Map column names
    """
        data = (
            self.loader.from_huggingface(self.hugginface_path, number_of_rows=self.number_of_rows)
            .with_columns(geometry_column="the_geom")
            .with_map({"Shape_STLe": "shape"})
        )
        assert isinstance(data.load(), gpd.GeoDataFrame)

        """
        Build method
    """
        loader = self.loader.from_huggingface(self.hugginface_path, number_of_rows=self.number_of_rows).with_columns(geometry_column="the_geom").with_crs(("EPSG:4326", "EPSG:2263")).with_map({"Shape_STLe": "shape"})
        assert loader.build() is not None

    def test_preview(self):
        loader = self.loader.from_file(self.csv_path).with_columns(
            geometry_column="the_geom"
        )

        assert loader.preview(format="ascii") is None

        assert loader.preview(format="json") is None
