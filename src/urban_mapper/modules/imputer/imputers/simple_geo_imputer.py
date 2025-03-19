from typing import Any

import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.imputer.abc_imputer import GeoImputerBase


@beartype
class SimpleGeoImputer(GeoImputerBase):
    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        _ = urban_layer
        return input_geodataframe.dropna(
            subset=[self.latitude_column, self.longitude_column]
        )

    def preview(self, format: str = "ascii") -> Any:
        if format == "ascii":
            return (
                f"Imputer: SimpleGeoImputer\n"
                f"  Action: Drop rows with missing '{self.latitude_column}' or '{self.longitude_column}'"
            )
        elif format == "json":
            return {
                "imputer": "SimpleGeoImputer",
                "action": "Drop rows with missing 'latitude' or 'longitude'",
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
