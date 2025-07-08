from typing import Any, Optional

import geopandas as gpd
import osmnx
import pandas as pd
from shapely.geometry import Point
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.imputer.abc_imputer import GeoImputerBase


@beartype
class AddressGeoImputer(GeoImputerBase):
    """Imputer that geocodes addresses to coordinates.

    !!! tip "What is that about?"
        Uses OpenStreetMap via `osmnx` to convert address strings into latitude and
        longitude values.

        You have an `address` / equivalent name column in your data, but no coordinates? Or missing coordinates?
        This imputer will geocode the addresses to fill in the missing latitude and longitude values.

    !!! tip "Understanding the extra parameters"
        If you look at the `GeoImputerBase`, addres_column_name is not a parameter there.
        As a result, below is an example localised around this primitive, but when using the factory,
        you will need to pass your `address` / equivalent name column to the kwards of `.on_columns(.)`.

        Examples:
        >>> import urban_mapper as um
        >>> factory = um.UrbanMapper().imputer.with_type("AddressGeoImputer")\
        ...     .on_columns(longitude_column="lng", latitude_column="lat", address_column="address")
        ...     # or .on_columns("lng", "lat", "address")
        >>> gdf = factory.transform(data_gdf, urban_layer)

    Attributes:
        latitude_column (str): Column for latitude values.
        longitude_column (str): Column for longitude values.
        address_column (str): Column with address strings.

    Examples:
        >>> from urban_mapper.modules.imputer import AddressGeoImputer
        >>> imputer = AddressGeoImputer(
        ...     latitude_column="lat",
        ...     longitude_column="lng",
        ...     address_column="address"
        ... )
        >>> geocoded_gdf = imputer.transform(data_gdf, urban_layer)

    !!! warning
        Requires an internet connection for geocoding via OpenStreetMap.
    """

    def __init__(
        self,
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        data_id: Optional[str] = None,
        address_column: Optional[str] = None,
    ):
        super().__init__(latitude_column, longitude_column, data_id)
        self.address_column = address_column

    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        """Geocode addresses into coordinates.

        Args:
            input_geodataframe: `GeoDataFrame` with address data.
            urban_layer: `Urban layer`.

        Returns:
            GeoDataFrame: Data with geocoded coordinates.

        !!! note
            Urban layer is included for interface compatibility but not used.
        """
        _ = urban_layer
        dataframe = input_geodataframe.copy()
        mask_missing = (
            dataframe[self.latitude_column].isna()
            | dataframe[self.longitude_column].isna()
        )
        missing_records = dataframe[mask_missing].copy()

        def geocode_address(row):
            address = str(row.get(self.address_column, "")).strip()
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
        """Preview the imputer configuration.

        Args:
            format: Output format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            Any: Configuration summary.

        Raises:
            ValueError: If format is unsupported.
        """
        if format == "ascii":
            lines = [
                f"Imputer: AddressGeoImputer",
                f"  Action: Impute '{self.latitude_column}' and '{self.longitude_column}' "
                f"using addresses from '{self.address_column}'",
            ]
            if self.data_id:
                lines.append(f"  Data ID: '{self.data_id}'")

            return "\n".join(lines)
        elif format == "json":
            return {
                "imputer": "AddressGeoImputer",
                "action": f"Impute '{self.latitude_column}' and '{self.longitude_column}' "
                f"using addresses from '{self.address_column}'",
                f"data_id": self.data_id,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
