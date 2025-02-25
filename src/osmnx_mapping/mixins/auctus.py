from typing import Union, List
import pandas as pd
import geopandas as gpd
from auctus_search import AuctusSearch, AuctusDatasetCollection


class AuctusSearchMixin(AuctusSearch):
    def explore_datasets_from_auctus(
        self,
        search_query: Union[str, List[str]],
        page: int = 1,
        size: int = 10,
        display_initial_results: bool = False,
    ) -> AuctusDatasetCollection:
        return self.search_datasets(
            search_query,
            page=page,
            size=size,
            display_initial_results=display_initial_results,
        )

    def load_dataset_from_auctus(
        self, display_table: bool = True
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        return self.load_selected_dataset(display_table)
