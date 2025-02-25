import geopandas as gpd
from beartype import beartype
from osmnx_mapping.modules.preprocessing.imputer.abc_imputer import GeoImputerBase


class SimpleGeoImputer(GeoImputerBase):
    @beartype
    def _transform(self, input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return input_geodataframe.dropna(
            subset=[self.latitude_column_name, self.longitude_column_name]
        )
