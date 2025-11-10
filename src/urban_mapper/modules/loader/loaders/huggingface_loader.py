import pandas as pd
import geopandas as gpd
from beartype import beartype
from typing import Union, Optional, Any, Tuple
from itertools import islice
import datasets
from thefuzz import process

from urban_mapper import logger
from urban_mapper.modules.loader.abc_loader import LoaderBase
from urban_mapper.config import DEFAULT_CRS
from .dataframe_loader import DataFrameLoader


@beartype
class HuggingFaceLoader(LoaderBase):
    """
    Load a dataset from `Hugging Face's Hub` using the `datasets` library.

    !!! info "What Are Hugging Face Datasets?"
        🤗 **Hugging Face Datasets** is your gateway to a vast list of datasets tailored for various application domains
        such as urban computing. In a nuthsell, this library simplifies data access, letting you load datasets
        with a single line of code.

        **How to Find and Use Datasets**: Head to the [Hugging Face Datasets Hub](https://huggingface.co/datasets),
        where you can search anything you like (e.g., "PLUTO" for NYC buildings information).

        For `from_huggingface`, you need the `repo_id` of the dataset you want to load. To find the `repo_id`, look for the
        `<namespace>/<dataset_name>` format in each card displaying / dataset's URL.
        For example, click on one of the card / dataset of interest, and lookup for the website's URL. E.g. `https://huggingface.co/datasets/oscur/pluto`,
        the `repo_id` is `oscur/pluto`. The `namespace` is the organisation or user who created the dataset,
        and the `dataset_name` is the specific dataset name.
        In this case, `oscur` is the namespace and `pluto` is the dataset name.

    !!! success "OSCUR: Pioneering Urban Science"
        🌍 **OSCUR** (Open-Source Cyberinfrastructure for Urban Computing) integrates tools for data exploration,
        analytics, and machine learning, all while fostering a collaborative community to advance urban science.

        All datasets used by any of the initiatives under OSCUR are open-source and available on Hugging Face
        Datasets Hub. As `UrbanMapper` is one of the initiatives under OSCUR, all datasets throughout our examples
        and case studies are available under the `oscur` namespace.

        Feel free to explore our datasets, at [https://huggingface.co/oscur](https://huggingface.co/oscur).

        Load them easily:
        ```python
        loader = mapper.loader.from_huggingface("oscur/taxisvis1M")
        ```

        Dive deeper at [oscur.org](https://oscur.org/) for other open-source initiatives and tools.

    !!! warning "Potential Errors Explained"
        Mistakes happen—here’s what might go wrong and how we help:

        If `repo_id` is invalid, a `ValueError` pops up with smart suggestions powered by
        [TheFuzz](https://github.com/seatgeek/thefuzz), a fuzzy matching library. We compare your input to
        existing datasets and offer the closest matches:

        - **No Slash (e.g., `plutoo`)**: Assumes it’s a dataset name and suggests full `repo_id`s (e.g., `oscur/pluto`). Or closest matches.
        - **Bad Namespace (e.g., `oscurq/pluto`)**: If the namespace doesn’t exist, we suggest similar ones (e.g., `oscur`).
        - **Bad Dataset Name (e.g., `oscur/plutoo`)**: If the namespace is valid but the dataset isn’t, we suggest close matches.

        Errors come with context—like available datasets in a namespace—so you can fix it fast.

    Args:
        repo_id (str): The dataset repository ID on Hugging Face.
        number_of_rows (Optional[int]): Number of rows to load. Defaults to None.
        streaming (Optional[bool]): Whether to use streaming mode. Defaults to False.
        debug_limit_list_datasets (Optional[int]): Limit on datasets fetched for error handling. Defaults to None.

    Returns:
        LoaderFactory: The updated LoaderFactory instance for method chaining.

    Raises:
        ValueError: If the dataset cannot be loaded due to an invalid `repo_id` or other issues.

    Examples:
        >>> # Load a full dataset
        >>> loader = mapper.loader.from_huggingface("oscur/pluto")
        >>> gdf = loader.load()
        >>> print(gdf.head())  # Next steps: analyze or visualize the data

        >>> # Load 500 rows with streaming (i.e without loading the entire dataset)
        >>> loader = mapper.loader.from_huggingface("oscur/NYC_311", number_of_rows=500, streaming=True)
        >>> gdf = loader.load()
        >>> print(gdf.head())  # Next steps: process the loaded subset

        >>> # Load 1000 rows without streaming
        >>> loader = mapper.loader.from_huggingface("oscur/taxisvis1M", number_of_rows=1000)
        >>> gdf = loader.load()
        >>> print(gdf.head())  # Next steps: explore the sliced data

        >>> # Handle typo in namespace
        >>> try:
        ...     loader = mapper.loader.from_huggingface("oscurq/pluto")
        ... except ValueError as e:
        ...     print(e)
        ValueError: The repository 'oscurq' does not exist on Hugging Face. Maybe you meant one of these:
        - oscur (similarity: 90%)
        - XXX (similarity: 85%)

        >>> # Handle typo in dataset name
        >>> try:
        ...     loader = mapper.loader.from_huggingface("oscur/plutoo")
        ... except ValueError as e:
        ...     print(e)
        ValueError: The dataset 'plutoo' does not exist in repository 'oscur'. Maybe you meant one of these:
        - oscur/pluto (similarity: 90%)
        - XXX (similarity: 80%)

        >>> # Handle input without namespace
        >>> try:
        ...     loader = mapper.loader.from_huggingface("plutoo")
        ... except ValueError as e:
        ...     print(e)
        ValueError: The dataset 'plutoo' does not exist on Hugging Face. Maybe you meant one of these:
        - oscur/pluto (similarity: 90%)
        - XXX (similarity: 85%)

    """

    def __init__(
        self,
        repo_id: str,
        number_of_rows: Optional[int] = None,
        streaming: Optional[bool] = False,
        debug_limit_list_datasets: Optional[int] = None,
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        geometry_column: Optional[str] = None,
        coordinate_reference_system: Union[str, Tuple[str, str]] = DEFAULT_CRS,
        **additional_loader_parameters: Any,
    ) -> None:
        super().__init__(
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            geometry_column=geometry_column,
            coordinate_reference_system=coordinate_reference_system,
            **additional_loader_parameters,
        )
        self.repo_id = repo_id
        self.number_of_rows = number_of_rows
        self.streaming = streaming
        self.debug_limit_list_datasets = debug_limit_list_datasets
        self.source_data = None

    def _load(self) -> gpd.GeoDataFrame:
        try:
            if self.number_of_rows:
                if self.streaming:
                    # Use streaming mode to fetch only the required rows
                    dataset = datasets.load_dataset(
                        self.repo_id, split="train", streaming=True
                    )
                    limited_rows = list(islice(dataset, self.number_of_rows))
                    self.source_data = pd.DataFrame(limited_rows)
                    logger.log(
                        "DEBUG_LOW",
                        f"Loaded {self.number_of_rows} rows in streaming mode from {self.repo_id}.",
                    )
                else:
                    # Use slicing with split for non-streaming mode
                    dataset = datasets.load_dataset(
                        self.repo_id, split=f"train[:{self.number_of_rows}]"
                    )
                    self.source_data = pd.DataFrame(dataset)
                    logger.log(
                        "DEBUG_LOW",
                        f"Loaded {self.number_of_rows} rows from {self.repo_id}.",
                    )
            else:
                dataset = datasets.load_dataset(self.repo_id, split="train")
                self.source_data = pd.DataFrame(dataset)
                logger.log("DEBUG_LOW", f"Loaded dataset {self.repo_id}.")

            self.additional_loader_parameters.pop("input_dataframe", None)
            dataframe_loader = DataFrameLoader(
                input_dataframe=self.source_data,
                latitude_column=self.latitude_column,
                longitude_column=self.longitude_column,
                geometry_column=self.geometry_column,
                coordinate_reference_system=self.coordinate_reference_system,
                **self.additional_loader_parameters,
            )

            return dataframe_loader.load()

        except datasets.exceptions.DatasetNotFoundError as e:
            dataset_dict = self._build_dataset_dict(
                limit=self.debug_limit_list_datasets
            )
            if "/" not in self.repo_id:
                all_datasets = [
                    f"{repo}/{ds}"
                    for repo, ds_list in dataset_dict.items()
                    for ds in ds_list
                ]
                matches = process.extract(
                    self.repo_id,
                    all_datasets,
                    processor=lambda x: x.split("/")[-1] if "/" in x else x,
                )
                filtered_matches = [
                    (match, score) for match, score in matches if score > 80
                ]
                top_matches = filtered_matches[:10]
                suggestions = [
                    f"{match} (similarity: {score}%)" for match, score in top_matches
                ]
                suggestion_text = (
                    " Maybe you meant one of these:\n" + "\n".join(suggestions)
                    if suggestions
                    else ""
                )
                raise ValueError(
                    f"The dataset '{self.repo_id}' does not exist on Hugging Face. "
                    f"Please verify the dataset ID.{suggestion_text}"
                ) from e
            else:
                repo_name, dataset_name = self.repo_id.split("/", 1)
                if repo_name not in dataset_dict:
                    all_repos = list(dataset_dict.keys())
                    matches = process.extract(repo_name, all_repos, limit=1000)
                    filtered_matches = [
                        (match, score) for match, score in matches if score > 80
                    ]
                    top_matches = filtered_matches[:10]
                    suggestions = [
                        f"{match} (similarity: {score}%)"
                        for match, score in top_matches
                    ]
                    suggestion_text = (
                        " Maybe you meant one of these:\n" + "\n".join(suggestions)
                        if suggestions
                        else ""
                    )
                    raise ValueError(
                        f"The repository '{repo_name}' does not exist on Hugging Face. "
                        f"Please verify the repository name.{suggestion_text}"
                    ) from e
                else:
                    available_datasets = dataset_dict[repo_name]
                    matches = process.extract(
                        dataset_name, available_datasets, limit=None
                    )
                    filtered_matches = [
                        (match, score) for match, score in matches if score > 80
                    ]
                    top_matches = filtered_matches[:10]
                    suggestions = [
                        f"{repo_name}/{match} (similarity: {score}%)"
                        for match, score in top_matches
                    ]
                    suggestion_text = (
                        " Maybe you meant one of these:\n" + "\n".join(suggestions)
                        if suggestions
                        else ""
                    )
                    raise ValueError(
                        f"The dataset '{dataset_name}' does not exist in repository '{repo_name}'. "
                        f"Available datasets: {', '.join(available_datasets)}.{suggestion_text}"
                    ) from e

        except Exception as e:
            raise ValueError(f"Error loading dataset '{self.repo_id}': {str(e)}") from e

    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of this `DataFrameLoader` loader.

        Creates a summary representation of the loader for quick inspection.

        Args:
            format: The output format for the preview. Options include:

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use

        Returns:
            A string or dictionary representing the loader, depending on the format.

        Raises:
            ValueError: If an unsupported format is requested.
        """
        if format == "ascii":
            return (
                f"Loader: DataFrameLoader\n"
                f"  Latitude Column: {self.latitude_column}\n"
                f"  Longitude Column: {self.longitude_column}\n"
                f"  Geometry Column: {self.geometry_column}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Additional params: {self.additional_loader_parameters}\n"
            )
        elif format == "json":
            return {
                "loader": "DataFrameLoader",
                "latitude_column": self.latitude_column,
                "longitude_column": self.longitude_column,
                "geometry_column": self.geometry_column,
                "crs": self.coordinate_reference_system,
                "additional_params": self.additional_loader_parameters,
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
