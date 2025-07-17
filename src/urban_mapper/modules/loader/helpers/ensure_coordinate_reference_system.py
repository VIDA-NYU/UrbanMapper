from typing import Callable, Union, Tuple
import geopandas as gpd
from beartype import beartype

from urban_mapper.config import DEFAULT_CRS


@beartype
def ensure_coordinate_reference_system(
    function_to_wrap: Callable[..., gpd.GeoDataFrame],
) -> Callable[..., gpd.GeoDataFrame]:
    def wrapper(self, *args, **kwargs) -> gpd.GeoDataFrame:
        loaded_geodataframe: gpd.GeoDataFrame = function_to_wrap(self, *args, **kwargs)
        target_coordinate_reference_system: Union[str, Tuple[str, str]] = getattr(
            self, "coordinate_reference_system", DEFAULT_CRS
        )

        target_coordinate_reference_system = (
            target_coordinate_reference_system[1]
            if isinstance(target_coordinate_reference_system, tuple)
            else target_coordinate_reference_system
        )

        if loaded_geodataframe.crs is None:
            loaded_geodataframe.set_crs(
                target_coordinate_reference_system, inplace=True
            )
        elif loaded_geodataframe.crs.to_string() != target_coordinate_reference_system:
            loaded_geodataframe = loaded_geodataframe.to_crs(
                target_coordinate_reference_system
            )

        return loaded_geodataframe

    return wrapper
