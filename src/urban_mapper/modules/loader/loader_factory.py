import json
from collections import defaultdict
from pathlib import Path
from typing import Optional, Union, Dict, Tuple

import geopandas as gpd
import huggingface_hub
import pandas as pd
from beartype import beartype

from urban_mapper import logger
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.modules.loader.abc_loader import LoaderBase
from urban_mapper.modules.loader.loaders.csv_loader import CSVLoader
from urban_mapper.modules.loader.loaders.parquet_loader import ParquetLoader
from urban_mapper.modules.loader.loaders.shapefile_loader import ShapefileLoader
from urban_mapper.modules.loader.loaders.dataframe_loader import DataFrameLoader
from urban_mapper.modules.loader.loaders.huggingface_loader import HuggingFaceLoader
from urban_mapper.utils import require_attributes

LOADER_FACTORY = {
    ".csv": {"class": CSVLoader, "requires_columns": True},
    ".shp": {"class": ShapefileLoader, "requires_columns": False},
    ".parquet": {"class": ParquetLoader, "requires_columns": True},
    "dataframe": {"class": DataFrameLoader, "requires_columns": True},
    "huggingface": {"class": HuggingFaceLoader, "requires_columns": True},
}


@beartype
class LoaderFactory:
    """Factory class for creating and configuring data loaders.
    
    This class implements a fluent chaining methods-based interface for creating and configuring data loaders.

    The factory manages the details of `loader instantiation`, `coordinate reference system`
    conversion, `column mapping`, and other data loading concerns, providing a consistent
    interface regardless of the underlying data source.
    
    Attributes:
        source_type: The type of data source ("file" or "dataframe").
        source_data: The actual data source (file path or dataframe).
        latitude_column: The name of the column containing latitude values.
        longitude_column: The name of the column containing longitude values.
        crs: The coordinate reference system to use for the loaded data.
        _instance: The underlying loader instance (internal use only).
        _preview: Preview configuration (internal use only).
        
    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> 
        >>> # Initialise UrbanMapper
        >>> mapper = UrbanMapper()
        >>> 
        >>> # Load data from a CSV file with coordinate columns
        >>> gdf = (
        ...         mapper.loader\\
        ...         .from_file("your_file_path.csv")\\
        ...         .with_columns(longitude_column="lon", latitude_column="lat")\\
        ...         .load()
        ...     )
        >>>
        >>> # Load data from a GeoDataFrame
        >>> import geopandas as gpd
        >>> existing_data = gpd.read_file("data/some_shapefile.shp")
        >>> gdf = mapper.loader.from_dataframe(existing_data).load() # Concise inline manner
    """

    def __init__(self):
        self.source_type: Optional[str] = None
        self.source_data: Optional[Union[str, pd.DataFrame, gpd.GeoDataFrame]] = None
        self.latitude_column: Optional[str] = None
        self.longitude_column: Optional[str] = None
        self.map_columns: Optional[Dict[str, str]] = None
        self.geometry_column: Optional[str] = None
        self.crs: Union[str, Tuple[str, str]] = DEFAULT_CRS
        self._instance: Optional[LoaderBase] = None
        self._preview: Optional[dict] = None
        self._columns_configured: bool = False

    def _reset(self):
        self.source_type = None
        self.source_data = None
        self.latitude_column = None
        self.longitude_column = None
        self.map_columns = None
        self.geometry_column = None
        self.crs = DEFAULT_CRS
        self.repo_id = None
        self.number_of_row = None
        self.streaming = False
        self.debug_limit_list_datasets = None
        self._instance = None
        self._preview = None
        self._columns_configured = False

    def from_file(self, file_path: str) -> "LoaderFactory":
        """Configure the factory to load data from a file.

        This method sets up the factory to load data from a file path. The file format
        is determined by the file extension. Supported formats include `CSV`, `shapefile`,
        and `Parquet`.

        Args:
            file_path: Path to the data file to load.

        Returns:
            The LoaderFactory instance for method chaining.

        Examples:
            >>> loader = mapper.loader.from_file("data/points.csv")
            >>> # Next steps would typically be to call with_columns() and load()
        """
        self._reset()
        self.source_type = "file"
        self.source_data = file_path
        logger.log(
            "DEBUG_LOW",
            f"FROM_FILE: Initialised LoaderFactory with file_path={file_path}",
        )
        return self

    def from_dataframe(
        self, dataframe: Union[pd.DataFrame, gpd.GeoDataFrame]
    ) -> "LoaderFactory":
        """Configure the factory to load data from an existing dataframe.

        This method sets up the factory to load data from a pandas `DataFrame` or
        geopandas `GeoDataFrame`. For `DataFrames` without geometry, you will need
        to call `with_columns()` to specify the latitude and longitude columns.

        Args:
            dataframe: The pandas DataFrame or geopandas GeoDataFrame to load.

        Returns:
            The LoaderFactory instance for method chaining.

        Examples:
            >>> import pandas as pd
            >>> df = pd.read_csv("data/points.csv")
            >>> loader = mapper.loader.from_dataframe(df)
            >>> # For regular DataFrames, you must specify coordinate columns:
            >>> loader.with_columns(longitude_column="lon", latitude_column="lat")
        """
        self._reset()
        self.source_type = "dataframe"
        self.source_data = dataframe
        logger.log(
            "DEBUG_LOW",
            f"FROM_DATAFRAME: Initialised LoaderFactory with dataframe={dataframe}",
        )
        return self

    def _build_dataset_dict(self, limit: Optional[int] = None):
        all_datasets = [
            dataset.id
            for dataset in (
                huggingface_hub.list_datasets(limit=limit)
                if limit
                else huggingface_hub.list_datasets()
            )
        ]
        dataset_dict = defaultdict(list)
        for dataset_id in all_datasets:
            if "/" in dataset_id:
                repo_name, dataset_name = dataset_id.split("/", 1)
                dataset_dict[repo_name].append(dataset_name)
        return dataset_dict

    def from_huggingface(
        self,
        repo_id: str,
        number_of_rows: Optional[int] = None,
        streaming: Optional[bool] = False,
        debug_limit_list_datasets: Optional[int] = None,
    ) -> "LoaderFactory":
        self._reset()
        self.source_type = "huggingface"
        self.source_data = repo_id
        self.repo_id = repo_id
        self.number_of_row = number_of_rows
        self.streaming = streaming
        self.debug_limit_list_datasets = debug_limit_list_datasets

        logger.log(
            "DEBUG_LOW",
            f"FROM_HUGGINGFACE: Loaded dataset {repo_id} with "
            f"{'all rows' if number_of_rows is None else number_of_rows} rows "
            f"{'(streaming mode)' if streaming else '(non-streaming mode)'}.",
        )
        return self

    def with_columns(
        self,
        longitude_column: Optional[str] = None,
        latitude_column: Optional[str] = None,
        geometry_column: Optional[str] = None,
    ) -> "LoaderFactory":
        """Specify either the latitude and longitude columns or a single geometry column in the data source.

        This method configures which columns in the data source contain the latitude,
        longitude coordinates, or geometry data. Either both `latitude_column` and
        `longitude_column` must be set, or `geometry_column` must be set.
        
        Args:
            longitude_column: Name of the column containing longitude values (optional).
            latitude_column: Name of the column containing latitude values (optional).
            geometry_column: Name of the column containing geometry data (optional).
            
        Returns:
            The LoaderFactory instance for method chaining.
            
        Examples:
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(geometry_column="geom")
        """
        if self._columns_configured:
            raise ValueError(
                "with_columns has already been configured for this loader. "
                "Each loader instance can only define one coordinate configuration "
                "(for example choose either pickup or dropoff coordinates when working "
                "with taxi trips). Create a new loader to configure another set of coordinates."
            )
        self.latitude_column = latitude_column
        self.longitude_column = longitude_column
        self.geometry_column = geometry_column
        if any(
            value is not None
            for value in (latitude_column, longitude_column, geometry_column)
        ):
            self._columns_configured = True
        logger.log(
            "DEBUG_LOW",
            f"WITH_COLUMNS: Initialised LoaderFactory "
            f"with either latitude_column={latitude_column} and longitude_column={longitude_column} or geometry_column={geometry_column}",
        )
        return self

    def with_crs(
        self, crs: Union[str, Tuple[str, str]] = DEFAULT_CRS
    ) -> "LoaderFactory":
        """Specify the coordinate reference system for the loaded data.
        
        This method configures the `coordinate reference system (CRS)` to use for the loaded
        data. If the source data already has a `CRS`, it will be converted to the specified `CRS`.
        
        Args:
            crs: The coordinate reference system to use, in any format accepted by geopandas
                (default: `EPSG:4326`, which is standard `WGS84` coordinates).
                If a string, it specifies the coordinate reference system to use (default: 'EPSG:4326').
                If a tuple (source_crs, target_crs), it defines a conversion from the source CRS to the target CRS (default target CRS: 'EPSG:4326').

            
        Returns:
            The LoaderFactory instance for method chaining.
            
        Examples:
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")\
            ...     .with_crs("EPSG:3857")  # Use Web Mercator projection
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")\
            ...     .with_crs( ("EPSG:2263", "EPSG:3857") )  # Use NY State Plane to load data and convert them to Web Mercator projection
        """
        self.crs = crs
        logger.log(
            "DEBUG_LOW",
            f"WITH_CRS: Initialised LoaderFactory with crs={crs}",
        )
        return self

    def with_map(
        self,
        map_columns: Dict[str, str],
    ) -> "LoaderFactory":
        """Specify a set of source-target to map column names.
        
        This method configures which columns in the data source should have column names changed.
        
        Args:
            map_columns: dictionary with source-target (key-value) columns to map from source to target names.
            
        Returns:
            The LoaderFactory instance for method chaining.
            
        Examples:
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_map(map_columns={"long": "longitude", "lat": "latitude"})
        """
        self.map_columns = map_columns
        logger.log(
            "DEBUG_LOW",
            f"WITH_MAP: Initialised LoaderFactory with map_columns={map_columns}",
        )
        return self

    @require_attributes(["source_type", "source_data"])
    def load(self) -> gpd.GeoDataFrame:
        """Load the data and return it as a `GeoDataFrame`.
        
        This method loads the data from the configured source and returns it as a
        geopandas `GeoDataFrame`. It handles the details of loading from different
        source types and formats.
                
        Returns:
            A GeoDataFrame containing the loaded data.
            
        Raises:
            ValueError: If the source type is invalid, the file format is unsupported,
                or required parameters (like latitude/longitude columns) are missing.
                
        Examples:
            >>> # Load CSV data
            >>> gdf = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")\
            ...     .load()
            >>> 
            >>> # Load shapefile data
            >>> gdf = mapper.loader.from_file("data/boundaries.shp").load()
        """
        self.build()
        return self._instance.load()

    def build(self) -> LoaderBase:
        """Build and return a `loader` instance without loading the data.
        
        This method creates and returns a loader instance without immediately loading
        the data. It is primarily intended for use in the `UrbanPipeline`, where the
        actual loading is deferred until pipeline execution.
        
        Returns:
            A LoaderBase instance configured to load the data when needed.
            
        Raises:
            ValueError: If the source type is not supported, the file format is unsupported,
                or required parameters (like latitude/longitude columns) are missing.
                
        Note:
            For most use cases outside of pipelines, using load() is preferred as it
            directly returns the loaded data.
            
        Examples:
            >>> # Creating a pipeline component
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")\
            ...     .build()
            >>> step_loader_for_pipeline = ("My Loader", loader) # Add this in the list of steps in the `UrbanPipeline`.
        """
        logger.log(
            "DEBUG_MID",
            "WARNING: build() should only be used in UrbanPipeline. "
            "In other cases, using .load() is a better option.",
        )
        has_geometry = self.geometry_column is not None
        has_lat_or_long = (
            self.latitude_column is not None or self.longitude_column is not None
        )
        has_lat_and_long = (
            self.latitude_column is not None and self.longitude_column is not None
        )
        file_path = ""
        loader_class = None
        input_data = None

        if self.source_type == "file":
            file_path = self.source_data
            file_ext = Path(self.source_data).suffix.lower()
            if file_ext not in LOADER_FACTORY:
                raise ValueError(f"Unsupported file format: {file_ext}")
            loader_info = LOADER_FACTORY[file_ext]
            if loader_info["requires_columns"] and (
                (has_geometry and has_lat_or_long)
                or (not has_geometry and not has_lat_and_long)
            ):
                raise ValueError(
                    f"Loader for {file_ext} requires latitude and longitude columns or only geometry column. Call with_columns() with valid column names."
                )
            loader_class = loader_info["class"]
        elif self.source_type == "dataframe":
            if (has_geometry and has_lat_or_long) or (
                not has_geometry and not has_lat_and_long
            ):
                raise ValueError(
                    "DataFrame loading requires latitude and longitude columns or only geometry column. Call with_columns() with valid column names."
                )
            loader_class = LOADER_FACTORY[self.source_type]["class"]
            input_data = self.source_data.copy()
        elif self.source_type == "huggingface":
            if (has_geometry and has_lat_or_long) or (
                not has_geometry and not has_lat_and_long
            ):
                raise ValueError(
                    "Hugging Face dataset loading requires latitude and longitude columns or only geometry column. "
                    "Call with_columns() with valid column names."
                )
            loader_class = LOADER_FACTORY[self.source_type]["class"]
        else:
            raise ValueError("Invalid source type.")

        self._instance = loader_class(
            latitude_column=self.latitude_column,
            longitude_column=self.longitude_column,
            geometry_column=self.geometry_column,
            coordinate_reference_system=self.crs,
            map_columns=self.map_columns,
            ## specific to FileLoaders (CSVLoader, ParquetLoader, and ShapefileLoader)
            file_path=file_path,
            ## specific to DataFrameLoader
            input_dataframe=input_data,
            ## specific to HuggingFaceLoader
            repo_id=self.repo_id,
            number_of_rows=self.number_of_row,
            streaming=self.streaming,
            debug_limit_list_datasets=self.debug_limit_list_datasets,
        )
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance

    def preview(self, format="ascii") -> None:
        """Display a preview of the `loader` configuration and settings.
        
        This method generates and displays a preview of the `loader`, showing its
        `configuration`, `settings`, and `other metadata`. The preview can be displayed
        in different formats.
        
        Args:
            format: The format to display the preview in (default: "ascii").

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use
                
        Raises:
            ValueError: If an unsupported format is specified.
            
        Note:
            This method requires a loader instance to be available. Call load()
            or build() first to create an instance.
            
        Examples:
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")
            >>> # Preview after loading data
            >>> loader.load()
            >>> loader.preview()
            >>> # Or JSON format
            >>> loader.preview(format="json")
        """
        if self._instance is None:
            logger.log(
                "DEBUG_LOW",
                "No loader instance available to preview. Call load() first.",
            )
            return

        if hasattr(self._instance, "preview"):
            preview_data = self._instance.preview(format=format)
            if format == "ascii":
                print(preview_data)
            elif format == "json":
                print(json.dumps(preview_data, indent=2))
            else:
                raise ValueError(f"Unsupported format '{format}'.")
        else:
            logger.log("DEBUG_LOW", "Preview not supported for this loader's instance.")

    def with_preview(self, format="ascii") -> "LoaderFactory":
        """Configure the factory to display a preview after loading or building.
        
        This method configures the factory to automatically display a preview after
        loading data with `load()` or building a loader with `build()`. It's a convenient
        way to inspect the loader configuration and the loaded data.
        
        Args:
            format: The format to display the preview in (default: "ascii").

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use
                
        Returns:
            The LoaderFactory instance for method chaining.
            
        Examples:
            >>> # Auto-preview after loading
            >>> gdf = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")\
            ...     .with_preview(format="json")\
            ...     .load()
        """
        self._preview = {
            "format": format,
        }
        return self
