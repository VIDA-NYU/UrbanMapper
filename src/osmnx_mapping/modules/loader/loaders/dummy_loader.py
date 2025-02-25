import geopandas as gpd
from beartype import beartype
from osmnx_mapping.modules.loader.abc_loader import LoaderBase


@beartype
class DummyLoader(LoaderBase):
    def _load_data(self) -> gpd.GeoDataFrame:
        raise NotImplementedError(
            "DummyLoader does not support file loading. Use load_data_from_dataframe instead."
        )
