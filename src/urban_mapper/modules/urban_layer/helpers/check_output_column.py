from typing import Callable, Tuple
import geopandas as gpd
import pandas as pd
from beartype import beartype


@beartype
def check_output_column(
    function_to_wrap: Callable[..., Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]],
) -> Callable[..., Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]]:
    def wrapper(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str | None = None,
        latitude_column: str | None = None,
        output_column: str | None = None,
        threshold_distance: float | None = None,
        reset_output_column: bool = False,
        *args,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        if reset_output_column and output_column in data.columns:
            data = data.drop(columns=output_column)
        if output_column in data.columns:
            raise ValueError(
                f"GeoDataFrame already contains column '{output_column}'. "
                "Please update the parameter 'output_column'."
            )
        if longitude_column and not pd.api.types.is_numeric_dtype(
            data[latitude_column]
        ):
            data[latitude_column] = pd.to_numeric(
                data[latitude_column], errors="coerce"
            )
        if longitude_column and not pd.api.types.is_numeric_dtype(
            data[longitude_column]
        ):
            data[longitude_column] = pd.to_numeric(
                data[longitude_column], errors="coerce"
            )
        return function_to_wrap(
            self,
            data,
            longitude_column,
            latitude_column,
            output_column,
            threshold_distance,
            reset_output_column,
            *args,
            **kwargs,
        )

    return wrapper
