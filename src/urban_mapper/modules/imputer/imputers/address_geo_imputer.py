from typing import Any

import geopandas as gpd
import osmnx
import pandas as pd
from shapely.geometry import Point
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.imputer.abc_imputer import GeoImputerBase


@beartype
class AddressGeoImputer(GeoImputerBase):
    def __init__(
        self,
        latitude_column: str,
        longitude_column: str,
        address_column_name: str,
    ):
        super().__init__(latitude_column, longitude_column)
        self.latitude_column = latitude_column
        self.longitude_column = longitude_column
        self.address_column_name = address_column_name

    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        _ = urban_layer
        dataframe = input_geodataframe.copy()
        mask_missing = (
            dataframe[self.latitude_column].isna()
            | dataframe[self.longitude_column].isna()
        )
        missing_records = dataframe[mask_missing].copy()

        def geocode_address(row):
            address = str(row.get(self.address_column_name, "")).strip()
            if not address:
                return None
            try:
                latitude_longitude = osmnx.geocode(address)
                if not latitude_longitude:
                    return None
                latitude_value, longitude_value = latitude_longitude
                return pd.Series(
                    {
                        self.latitude_column: latitude_value,
                        self.longitude_column: longitude_value,
                        "geometry": Point(longitude_value, latitude_value),
                    }
                )
            except Exception:
                return None

        geocoded_data = missing_records.apply(geocode_address, axis=1)
        valid_indices = geocoded_data.dropna().index

        if not valid_indices.empty:
            dataframe.loc[valid_indices] = geocoded_data.loc[valid_indices]

        dataframe = dataframe.loc[~mask_missing | dataframe.index.isin(valid_indices)]
        return dataframe

    def preview(self, format: str = "ascii") -> Any:
        if format == "ascii":
            return (
                f"Imputer: AddressGeoImputer\n"
                f"  Action: Impute '{self.latitude_column}' and '{self.longitude_column}' "
                f"using addresses from '{self.address_column_name}'"
            )
        elif format == "json":
            return {
                "imputer": "AddressGeoImputer",
                "action": f"Impute '{self.latitude_column}' and '{self.longitude_column}' "
                f"using addresses from '{self.address_column_name}'",
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
