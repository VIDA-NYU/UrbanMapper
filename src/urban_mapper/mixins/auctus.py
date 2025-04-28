from typing import Union, List
import pandas as pd
import geopandas as gpd
from auctus_search import AuctusSearch, AuctusDatasetCollection


class AuctusSearchMixin(AuctusSearch):
    """Mixin for searching, exploring, and loading datasets from the `Auctus data discovery` service.

    This mixin extends `AuctusSearch` to provide a simplified interface for discovering
    and working with datasets from the `Auctus data discovery service`. It allows users
    to search for relevant datasets, explore their metadata, and load them directly
    into their urban data analysis workflows.

    !!! question "What is Auctus?  What is Auctus Search?"
        `Auctus` is a web crawler and search engine for datasets, specifically meant for data augmentation tasks in
        machine learning. It is able to find datasets in different repositories and index them for later retrieval.

        `Auctus` paper's citation:
        > Sonia Castelo, Rémi Rampin, Aécio Santos, Aline Bessa, Fernando Chirigati, and Juliana Freire. 2021. Auctus: a dataset search engine for data discovery and augmentation. Proc. VLDB Endow. 14, 12 (July 2021), 2791–2794. https://doi.org/10.14778/3476311.3476346

        `Auctus` official website:
        > https://auctus.vida-nyu.org/

        Find more in the [Auctus GitHub repository](https://github.com/VIDA-NYU/auctus).

        –––

        `Auctus Search` on the other hand, is a wrapper of the great Auctus' API. Workable straightforwardly from
        a Jupyter notebook's cell.

        Find more in the [Auctus Search GitHub Repository](https://github.com/VIDA-NYU/auctus_search).

    !!! question "What is a mixin?"
        A mixin is a class that provides methods to other libraries' classes, but is not considered a base class itself.
        Consider this as helpers from external sources.

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>>
        >>> # Initialise UrbanMapper
        >>> mapper = UrbanMapper()
        >>>
        >>> # Search for datasets about NYC taxi trips
        >>> results = mapper.auctus.explore_datasets_from_auctus(
        ...     search_query="NYC taxi trips",
        ...     display_initial_results=True
        ... )
        >>>
        >>> # Select a dataset from the results (interactive)
        >>> # (This would be done through the UI that appears)
        >>>
        >>> # Load the selected dataset
        >>> taxi_trips = mapper.auctus.load_dataset_from_auctus()
        >>>
        >>> # Profile the dataset to understand its characteristics
        >>> mapper.auctus.profile_dataset_from_auctus()
    """

    def explore_datasets_from_auctus(
        self,
        search_query: Union[str, List[str]],
        page: int = 1,
        size: int = 10,
        display_initial_results: bool = False,
    ) -> AuctusDatasetCollection:
        """Search for datasets in the `Auctus data discovery service`.

        This method queries the `Auctus data discovery service` for datasets matching
        the provided search query. Results can be paginated and optionally displayed
        immediately for quick inspection.

        Args:
            search_query (Union[str, List[str]]): Search query string or list of strings to find datasets.
            page (int, optional): Page number for paginated results. Defaults to 1.
            size (int, optional): Number of results per page. Defaults to 10.
            display_initial_results (bool, optional): Whether to automatically display search results. Defaults to False.

        Returns:
            AuctusDatasetCollection: An object containing the search results, which can be further explored or used to select a dataset.

        Examples:
            >>> results = mapper.auctus.explore_datasets_from_auctus(
            ...     search_query="NYC crashes",
            ...     size=20,
            ...     display_initial_results=True
            ... )
        """
        return self.search_datasets(
            search_query,
            page=page,
            size=size,
            display_initial_results=display_initial_results,
        )

    def load_dataset_from_auctus(
        self, display_table: bool = True
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """Load the selected dataset from `Auctus search` results.

        This method loads the dataset that was selected after calling
        `explore_datasets_from_auctus()`. It can handle both tabular and geographic data,
        returning a pandas DataFrame or geopandas GeoDataFrame accordingly.

        Args:
            display_table (bool, optional): Whether to display a preview of the loaded data. Defaults to True.

        Returns:
            Union[pd.DataFrame, gpd.GeoDataFrame]: The loaded dataset, either as a pandas DataFrame or geopandas GeoDataFrame.

        Examples:
            >>> taxi_data = mapper.auctus.load_dataset_from_auctus(display_table=True)
        """
        return self.load_selected_dataset(display_table)

    def profile_dataset_from_auctus(self) -> None:
        """Generate and display a profile report for the selected Auctus dataset.

        This method creates a comprehensive profile of the dataset loaded using
        `load_dataset_from_auctus()`. The profile includes `statistics`, `distributions`,
        and insights into the dataset's characteristics, aiding in data understanding
        and preparation for analysis.

        Returns:
            None: This method does not return anything but displays the profile report.

        Examples:
            >>> mapper.auctus.profile_dataset_from_auctus()
        """
        self.profile_selected_dataset()
