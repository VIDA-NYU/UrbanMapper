from typing import Optional

import geopandas as gpd
import osmnx
import pandas as pd
from shapely.geometry import Point
from beartype import beartype
from osmnx_mapping.modules.preprocessing.imputer.abc_imputer import GeoImputerBase


class AddressGeoImputer(GeoImputerBase):
    @beartype
    def __init__(
        self,
        address_column_name: str,
        latitude_column_name: Optional[str] = None,
        longitude_column_name: Optional[str] = None,
    ) -> None:
        super().__init__(latitude_column_name, longitude_column_name)
        self.address_column_name = address_column_name

    @beartype
    def _transform(self, input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        dataframe = input_geodataframe.copy()

        if self.address_column_name not in dataframe.columns:
            raise ValueError(
                f"Column '{self.address_column_name}' not found in the input geodataframe."
            )

        mask_missing = (
            dataframe[self.latitude_column_name].isna()
            | dataframe[self.longitude_column_name].isna()
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
                        self.latitude_column_name: latitude_value,
                        self.longitude_column_name: longitude_value,
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
