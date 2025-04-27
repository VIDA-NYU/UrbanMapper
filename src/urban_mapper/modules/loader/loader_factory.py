import json
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import geopandas as gpd
from beartype import beartype

from urban_mapper.modules.loader.abc_loader import LoaderBase
from urban_mapper.modules.loader.loaders.csv_loader import CSVLoader
from urban_mapper.modules.loader.loaders.shapefile_loader import ShapefileLoader
from urban_mapper.modules.loader.loaders.parquet_loader import ParquetLoader
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.utils import require_attributes
from urban_mapper.utils.helpers.reset_attribute_before import reset_attributes_before
from urban_mapper import logger

FILE_LOADER_FACTORY = {
    ".csv": {"class": CSVLoader, "requires_columns": True},
    ".shp": {"class": ShapefileLoader, "requires_columns": False},
    ".parquet": {"class": ParquetLoader, "requires_columns": True},
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
        self.crs: str = DEFAULT_CRS
        self._instance: Optional[LoaderBase] = None
        self._preview: Optional[dict] = None

    @reset_attributes_before(
        ["source_type", "source_data", "latitude_column", "longitude_column"]
    )
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
        self.source_type = "file"
        self.latitude_column = None
        self.longitude_column = None
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
        self.source_type = "dataframe"
        self.source_data = dataframe
        self.latitude_column = "None"
        self.longitude_column = "None"
        logger.log(
            "DEBUG_LOW",
            f"FROM_DATAFRAME: Initialised LoaderFactory with dataframe={dataframe}",
        )
        return self

    def with_columns(
        self,
        longitude_column: str,
        latitude_column: str,
    ) -> "LoaderFactory":
        """Specify the latitude and longitude columns in the data source.
        
        This method configures which columns in the data source contain the latitude
        and longitude coordinates. This is required for `CSV` and `Parquet` files, as well
        as for `pandas DataFrames` without geometry.
        
        Args:
            longitude_column: Name of the column containing longitude values.
            latitude_column: Name of the column containing latitude values.
            
        Returns:
            The LoaderFactory instance for method chaining.
            
        Examples:
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")
        """
        self.latitude_column = latitude_column
        self.longitude_column = longitude_column
        logger.log(
            "DEBUG_LOW",
            f"WITH_COLUMNS: Initialised LoaderFactory "
            f"with latitude_column={latitude_column} and longitude_column={longitude_column}",
        )
        return self

    def with_crs(self, crs: str = DEFAULT_CRS) -> "LoaderFactory":
        """Specify the coordinate reference system for the loaded data.
        
        This method configures the `coordinate reference system (CRS)` to use for the loaded
        data. If the source data already has a `CRS`, it will be converted to the specified `CRS`.
        
        Args:
            crs: The coordinate reference system to use, in any format accepted by geopandas
                (default: `EPSG:4326`, which is standard `WGS84` coordinates).
            
        Returns:
            The LoaderFactory instance for method chaining.
            
        Examples:
            >>> loader = mapper.loader.from_file("data/points.csv")\
            ...     .with_columns(longitude_column="lon", latitude_column="lat")\
            ...     .with_crs("EPSG:3857")  # Use Web Mercator projection
        """
        self.crs = crs
        logger.log(
            "DEBUG_LOW",
            f"WITH_CRS: Initialised LoaderFactory with crs={crs}",
        )
        return self

    def _load_from_file(self, coordinate_reference_system: str) -> gpd.GeoDataFrame:
        file_path: str = self.source_data
        file_ext = Path(file_path).suffix.lower()
        loader_class = FILE_LOADER_FACTORY[file_ext]["class"]
        self._instance = loader_class(
            file_path,
            latitude_column=self.latitude_column,
            longitude_column=self.longitude_column,
            coordinate_reference_system=coordinate_reference_system,
        )
        return self._instance.load_data_from_file()

    def _load_from_dataframe(
        self, coordinate_reference_system: str
    ) -> gpd.GeoDataFrame:
        input_dataframe: Union[pd.DataFrame, gpd.GeoDataFrame] = self.source_data
        if isinstance(input_dataframe, gpd.GeoDataFrame):
            geo_dataframe: gpd.GeoDataFrame = input_dataframe.copy()
        else:
            geo_dataframe = gpd.GeoDataFrame(
                input_dataframe,
                geometry=gpd.points_from_xy(
                    input_dataframe[self.longitude_column],
                    input_dataframe[self.latitude_column],
                ),
                crs=coordinate_reference_system,
            )
        if geo_dataframe.crs is None:
            geo_dataframe.set_crs(coordinate_reference_system, inplace=True)
        elif geo_dataframe.crs.to_string() != coordinate_reference_system:
            geo_dataframe = geo_dataframe.to_crs(coordinate_reference_system)
        return geo_dataframe

    @require_attributes(["source_type", "source_data"])
    def load(self, coordinate_reference_system: str = DEFAULT_CRS) -> gpd.GeoDataFrame:
        """Load the data and return it as a `GeoDataFrame`.
        
        This method loads the data from the configured source and returns it as a
        geopandas `GeoDataFrame`. It handles the details of loading from different
        source types and formats.
        
        Args:
            coordinate_reference_system: The coordinate reference system to use for the
                loaded data (default: "EPSG:4326", which is standard WGS84 coordinates).
                
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
        if self.source_type == "file":
            file_ext = Path(self.source_data).suffix.lower()
            if file_ext not in FILE_LOADER_FACTORY:
                raise ValueError(f"Unsupported file format: {file_ext}")
            loader_info = FILE_LOADER_FACTORY[file_ext]
            if loader_info["requires_columns"] and (
                self.latitude_column is None or self.longitude_column is None
            ):
                raise ValueError(
                    f"Loader for {file_ext} requires latitude and longitude columns. Call with_columns() first."
                )
            loaded_data = self._load_from_file(coordinate_reference_system)
            if self._preview is not None:
                self.preview(format=self._preview["format"])
            return loaded_data
        elif self.source_type == "dataframe":
            if self.latitude_column == "None" or self.longitude_column == "None":
                raise ValueError(
                    "DataFrame loading requires latitude and longitude columns. Call with_columns() with valid column names."
                )
            loaded_data = self._load_from_dataframe(coordinate_reference_system)
            if self._preview is not None:
                logger.log(
                    "DEBUG_LOW",
                    "Note: Preview is not supported for DataFrame sources.",
                )
            return loaded_data
        else:
            raise ValueError("Invalid source type.")

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
        if self.source_type != "file":
            raise ValueError("Build only supports file sources for now.")
        file_ext = Path(self.source_data).suffix.lower()
        if file_ext not in FILE_LOADER_FACTORY:
            raise ValueError(f"Unsupported file format: {file_ext}")
        loader_info = FILE_LOADER_FACTORY[file_ext]
        loader_class = loader_info["class"]
        requires_columns = loader_info["requires_columns"]
        if requires_columns and (
            self.latitude_column is None or self.longitude_column is None
        ):
            raise ValueError(
                f"Loader for {file_ext} requires latitude and longitude columns. Call with_columns() first."
            )
        self._instance = loader_class(
            file_path=self.source_data,
            latitude_column=self.latitude_column,
            longitude_column=self.longitude_column,
            coordinate_reference_system=self.crs,
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
