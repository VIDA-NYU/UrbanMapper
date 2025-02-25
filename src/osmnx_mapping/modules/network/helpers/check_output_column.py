from typing import Callable
import geopandas as gpd
from beartype import beartype


@beartype
def check_output_column(
    function_to_wrap: Callable[..., gpd.GeoDataFrame],
) -> Callable[..., gpd.GeoDataFrame]:
    def wrapper(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_node",
        reset_output_column: bool = False,
        *args,
        **kwargs,
    ) -> gpd.GeoDataFrame:
        if reset_output_column and output_column in data.columns:
            data = data.drop(columns=output_column)
        if output_column in data.columns:
            raise ValueError(
                f"GeoDataFrame already contains column '{output_column}'. "
                "Please update the parameter 'output_column'."
            )
        return function_to_wrap(
            self,
            data,
            longitude_column,
            latitude_column,
            output_column,
            reset_output_column,
            *args,
            **kwargs,
        )

    return wrapper
