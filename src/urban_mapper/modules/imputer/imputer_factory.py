from typing import Optional, Dict, Any, Type, Union
import importlib
import inspect
import pkgutil
from pathlib import Path
from beartype import beartype
import geopandas as gpd
import json
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.utils.helpers import require_attributes_not_none
from .abc_imputer import GeoImputerBase
from ...utils.helpers.reset_attribute_before import reset_attributes_before
from urban_mapper import logger
from thefuzz import process

IMPUTER_REGISTRY: Dict[str, Type[GeoImputerBase]] = {}


@beartype
def register_imputer(name: str, imputer_class: Type[GeoImputerBase]) -> None:
    if not issubclass(imputer_class, GeoImputerBase):
        raise TypeError(f"{imputer_class} must be a subclass of GeoImputerBase")
    IMPUTER_REGISTRY[name] = imputer_class


@beartype
class ImputerFactory:
    """Factory for creating and configuring geographic imputers.

    Offers a fluent chaining-methods-based API to instantiate imputers, configure settings, and apply them.

    Attributes:
        _imputer_type (str): Type of imputer to create.
        _latitude_column (str): Column for latitude values.
        _longitude_column (str): Column for longitude values.

    Examples:
        >>> import urban_mapper as um
        >>> factory = um.UrbanMapper().imputer.with_type("SimpleGeoImputer")\
        ...     .on_columns(longitude_column="lng", latitude_column="lat")
        >>> gdf = factory.transform(data_gdf, urban_layer)
    """

    def __init__(self):
        self._data_id: Optional[str] = None
        self._imputer_type: Optional[str] = None
        self._latitude_column: Optional[str] = None
        self._longitude_column: Optional[str] = None
        self._extra_params: Dict[str, Any] = {}
        self._instance: Optional[GeoImputerBase] = None
        self._preview: Optional[dict] = None

    @reset_attributes_before(["_imputer_type", "_latitude_column", "_longitude_column"])
    def with_type(self, primitive_type: str) -> "ImputerFactory":
        """Set the imputer type to instantiate.

        Args:
            primitive_type: Imputer type (e.g., "SimpleGeoImputer").

        Returns:
            ImputerFactory: Self for chaining.

        Raises:
            ValueError: If primitive_type is not in IMPUTER_REGISTRY.

        !!! tip
            Check IMPUTER_REGISTRY keys for valid imputer types.
        """
        if self._imputer_type is not None:
            logger.log(
                "DEBUG_MID",
                f"WARNING: Imputer method already set to '{self._imputer_type}'. Overwriting.",
            )
            self._imputer_type = None

        if primitive_type not in IMPUTER_REGISTRY:
            available = list(IMPUTER_REGISTRY.keys())
            match, score = process.extractOne(primitive_type, available)
            if score > 80:
                suggestion = f" Maybe you meant '{match}'?"
            else:
                suggestion = ""
            raise ValueError(
                f"Unknown imputer method '{primitive_type}'. Available: {', '.join(available)}.{suggestion}"
            )
        self._imputer_type = primitive_type
        logger.log(
            "DEBUG_LOW",
            f"WITH_TYPE: Initialised ImputerFactory with imputer_type={primitive_type}",
        )
        return self

    def with_data(self, data_id: str) -> "ImputerFactory":
        """Set the data ID to perform impute.

        Args:
            data_id: ID of the dataset to be transformed.

        Returns:
            ImputerFactory: Self for chaining.

        Raises:
            ValueError: If primitive_type is not in IMPUTER_REGISTRY.

        !!! tip
            Check IMPUTER_REGISTRY keys for valid imputer types.
        """
        if self._data_id is not None:
            logger.log(
                "DEBUG_MID",
                f"WARNING: Data ID already set to '{self._data_id}'. Overwriting.",
            )
            self._data_id = None

        self._data_id = data_id
        logger.log(
            "DEBUG_LOW",
            f"WITH_DATA: Initialised ImputerFactory with data_id={data_id}",
        )
        return self

    def on_columns(
        self,
        longitude_column: str,
        latitude_column: str,
        **extra_params,
    ) -> "ImputerFactory":
        """Configure latitude and longitude columns.

        Args:
            longitude_column: Column name for longitude.
            latitude_column: Column name for latitude.
            **extra_params: Any other argument to be passed to a child class, such as address to `AddressGeoImputer`.

        Returns:
            ImputerFactory: Self for chaining.
        """
        self._longitude_column = longitude_column
        self._latitude_column = latitude_column
        self._extra_params = extra_params
        logger.log(
            "DEBUG_LOW",
            f"ON_COLUMNS: Initialised ImputerFactory with "
            f"longitude_column={longitude_column}, latitude_column={latitude_column}",
            f"extra_params={self._extra_params}",
        )
        return self

    @require_attributes_not_none(
        "_imputer_type",
        "_latitude_column",
        "_longitude_column",
    )
    def transform(
        self,
        input_geodataframe: Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame],
        urban_layer: UrbanLayerBase,
    ) -> Union[
        Dict[str, gpd.GeoDataFrame],
        gpd.GeoDataFrame,
    ]:
        """Apply the configured imputer to data.

        Args:
            input_geodataframe: one or more `GeoDataFrame` to process.
            urban_layer: Urban layer for context.

        Returns:
            Union[Dict[str, GeoDataFrame], GeoDataFrame]: Imputed data.

        Raises:
            ValueError: If configuration is incomplete.

        !!! note
            Call with_type() and on_columns() before transform().
        """
        imputer_class = IMPUTER_REGISTRY[self._imputer_type]
        self._instance = imputer_class(
            latitude_column=self._latitude_column,
            longitude_column=self._longitude_column,
            data_id=self._data_id,
            **self._extra_params,
        )

        if (
            isinstance(input_geodataframe, Dict)
            and self._data_id is not None
            and self._data_id not in input_geodataframe
        ):
            print(
                "WARNING: ",
                f"Data ID {self._data_id} was not found in the list of dataframes ",
                "No input transformation will be executed ",
            )

        return self._instance.transform(input_geodataframe, urban_layer)

    def build(self) -> GeoImputerBase:
        """Build and return an imputer instance without applying it.
        
        This method creates and returns an imputer instance without immediately applying
        it to data. It is primarily intended for use in the `UrbanPipeline`, where the
        actual imputation is deferred until pipeline execution.

        !!! note "To Keep In Mind"
            For most use cases outside of pipelines, using `transform()` is preferred as it
            directly applies the imputer and returns the imputed data.

        Returns:
            A GeoImputerBase instance configured and ready to use.
            
        Raises:
            ValueError: If the imputer type or latitude/longitude columns have not been specified.

        Examples:
            >>> # Creating a pipeline component
            >>> imputer_component = um.UrbanMapper().imputer.with_type("SimpleGeoImputer")\
            ...     .on_columns(longitude_column="lng", latitude_column="lat")\
            ...     .build()
            >>> pipeline.add_imputer(imputer_component)
        """
        logger.log(
            "DEBUG_MID",
            "WARNING: build() should only be used in UrbanPipeline. In other cases, "
            "using transform() is a better choice.",
        )
        if self._imputer_type is None:
            raise ValueError("Imputer type must be specified. Call with_type() first.")
        if self._latitude_column is None or self._longitude_column is None:
            raise ValueError(
                "Latitude and longitude columns must be specified. Call on_columns() first."
            )
        imputer_class = IMPUTER_REGISTRY[self._imputer_type]
        self._instance = imputer_class(
            latitude_column=self._latitude_column,
            longitude_column=self._longitude_column,
            data_id=self._data_id,
            **self._extra_params,
        )
        if self._preview is not None:
            self.preview(format=self._preview["format"])
        return self._instance

    def preview(self, format: str = "ascii") -> None:
        """Display a preview of the imputer configuration and settings.
        
        This method generates and displays a preview of the imputer, showing its
        configuration, settings, and other metadata. The preview can be displayed
        in different formats.
        
        Args:
            format: The format to display the preview in (default: "ascii").

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use
                
        Raises:
            ValueError: If an unsupported format is specified.
            
        Note:
            This method requires an imputer instance to be available. Call build()
            or transform() first to create an instance.
            
        Examples:
            >>> imputer = um.UrbanMapper().imputer.with_type("SimpleGeoImputer")\
            ...     .on_columns(longitude_column="lng", latitude_column="lat")
            >>> # Build the imputer instance
            >>> imputer.build()
            >>> # Display a preview
            >>> imputer.preview()
            >>> # Or in JSON format
            >>> imputer.preview(format="json")
        """
        if self._instance is None:
            print("No imputer instance available to preview. Call build() first.")
            return
        if hasattr(self._instance, "preview"):
            preview_data = self._instance.preview(format=format)
            if format == "ascii":
                print(preview_data)
            elif format == "json":
                print(json.dumps(preview_data, indent=2))
            else:
                raise ValueError(f"Unsupported format '{format}'")
        else:
            print("Preview not supported for this imputer instance.")

    def with_preview(self, format: str = "ascii") -> "ImputerFactory":
        """Configure the factory to display a preview after building.
        
        This method configures the factory to automatically display a preview after
        building an imputer with `build()`. It's a convenient way to inspect the imputer
        configuration without having to call `preview()` separately.
        
        Args:
            format: The format to display the preview in (default: "ascii").

                - [x] "ascii": Text-based format for terminal display
                - [x] "json": JSON-formatted data for programmatic use
                
        Returns:
            The ImputerFactory instance for method chaining.
            
        Examples:
            >>> # Auto-preview after building
            >>> imputer_component = um.UrbanMapper().imputer.with_type("SimpleGeoImputer")\
            ...     .on_columns(longitude_column="lng", latitude_column="lat")\
            ...     .with_preview(format="json")\
            ...     .build()
        """
        self._preview = {"format": format}
        return self


def _initialise():
    package_dir = Path(__file__).parent / "imputers"
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        try:
            module = importlib.import_module(
                f".imputers.{module_name}", package=__package__
            )
            for class_name, class_object in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(class_object, GeoImputerBase)
                    and class_object is not GeoImputerBase
                ):
                    register_imputer(class_name, class_object)
        except ImportError as error:
            raise ImportError(f"Failed to load imputers module {module_name}: {error}")


# Initialise the imputer registry when the module is imported
_initialise()
