from typing import Any

import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.loader.abc_loader import LoaderBase


@beartype
class ShapefileLoader(LoaderBase):
    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        gdf = gpd.read_file(self.file_path)

        if "geometry" not in gdf.columns:
            raise ValueError(
                "No geometry column found in shapefile. "
                "Standard shapefile format requires a geometry column."
            )

        if gdf.crs.to_string() != self.coordinate_reference_system:
            gdf = gdf.to_crs(self.coordinate_reference_system)

        if (
            not self.latitude_column
            or not self.longitude_column
            or gdf[self.latitude_column].isna().all()
            or gdf[self.longitude_column].isna().all()
        ):
            gdf["representative_points"] = gdf.geometry.representative_point()
            gdf["temporary_longitude"] = gdf["representative_points"].x
            gdf["temporary_latitude"] = gdf["representative_points"].y
            self.latitude_column = "temporary_latitude"
            self.longitude_column = "temporary_longitude"

        return gdf

    def preview(self, format: str = "ascii") -> Any:
        lat_col = self.latitude_column or "temporary_latitude (generated)"
        lon_col = self.longitude_column or "temporary_longitude (generated)"

        if format == "ascii":
            return (
                f"Loader: ShapefileLoader\n"
                f"  File: {self.file_path}\n"
                f"  Latitude Column: {lat_col}\n"
                f"  Longitude Column: {lon_col}\n"
                f"  CRS: {self.coordinate_reference_system}"
            )
        elif format == "json":
            return {
                "loader": "ShapefileLoader",
                "file": self.file_path,
                "latitude_column": lat_col,
                "longitude_column": lon_col,
                "crs": self.coordinate_reference_system,
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
