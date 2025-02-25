import geopandas as gpd
from beartype import beartype
from osmnx_mapping.modules.loader.abc_loader import LoaderBase


@beartype
class ShapefileLoader(LoaderBase):
    def _load_data(self) -> gpd.GeoDataFrame:
        gdf = gpd.read_file(self.file_path)

        if "geometry" not in gdf.columns:
            raise ValueError(
                "No geometry column found in shapefile. "
                "Standard shapefile format requires a geometry column."
            )

        if gdf.crs.to_string() != self.coordinate_reference_system:
            gdf = gdf.to_crs(self.coordinate_reference_system)

        if not self.latitude_column_name or not self.longitude_column_name:
            gdf["representative_points"] = gdf.geometry.representative_point()
            gdf["temporary_longitude"] = gdf["representative_points"].x
            gdf["temporary_latitude"] = gdf["representative_points"].y

            self.latitude_column_name = "temporary_latitude"
            self.longitude_column_name = "temporary_longitude"

        return gdf
