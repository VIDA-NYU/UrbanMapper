from abc import ABC, abstractmethod
from typing import Optional, Union, Dict, Any
import geopandas as gpd
from beartype import beartype

from urban_mapper.utils import require_arguments_not_none, require_attributes
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase


@beartype
class GeoImputerBase(ABC):
    """Abstract base class for geographic data imputers in `UrbanMapper`

    Provides the interface for `imputing` missing geographic data or `transforming` data
    into `coordinates`. Subclasses must implement the required methods to handle
    specific imputation tasks such as geocoding or spatial interpolation.

    Attributes:
        latitude_column (Optional[str]): Column name for latitude values post-imputation.
        longitude_column (Optional[str]): Column name for longitude values post-imputation.
        data_id (Optional[str]): Column name for processing specific values post-imputation.
        **extra_params: Any other argument used by a child class.

    !!! note
        This class is abstract and cannot be instantiated directly. Use concrete
        implementations like `SimpleGeoImputer` or `AddressGeoImputer`.
    """

    def __init__(
        self,
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        data_id: Optional[str] = None,
        **extra_params,
    ) -> None:
        self.data_id = data_id
        self.latitude_column = latitude_column
        self.longitude_column = longitude_column

    @abstractmethod
    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        """Internal method to impute geographic data.

        Called by `transform()` after validation. Subclasses must implement this method.

        !!! note "To be implemented by subclasses"
            This method should contain the core logic for imputing geographic data.
            It should handle the specific imputation task (e.g., geocoding, spatial
            interpolation) and return the modified `GeoDataFrame`.

        Args:
            input_geodataframe: GeoDataFrame with data to impute.
            urban_layer: Urban layer providing spatial context.

        Returns:
            GeoDataFrame: Data with imputed geographic information.

        Raises:
            ValueError: If imputation fails due to invalid inputs.

        !!! warning "Abstract Method"
            This method must be overridden in subclasses. Failure to implement will
            raise a NotImplementedError.
        """
        ...

    @require_arguments_not_none(
        "input_geodataframe", error_msg="Input GeoDataFrame cannot be None."
    )
    @require_arguments_not_none("urban_layer", error_msg="Urban layer cannot be None.")
    @require_attributes(["latitude_column", "longitude_column"])
    def transform(
        self,
        input_geodataframe: Union[Dict[str, gpd.GeoDataFrame], gpd.GeoDataFrame],
        urban_layer: UrbanLayerBase,
    ) -> Union[
        Dict[str, gpd.GeoDataFrame],
        gpd.GeoDataFrame,
    ]:
        """Public method to impute geographic data.

        Validates inputs and delegates to `_transform()` for imputation.

        !!! note "What to keep in mind here?"
            Every Imputer primitives (e.g. `AddressGeoImputer`, `SimpleGeoImputer`) should
            implement the `_transform()` method. This method is called by `transform()`
            after validating the inputs. The `_transform()` method is where the actual
            imputation logic resides. It should handle the specific imputation task
            (e.g., geocoding, spatial interpolation) and return the modified
            `GeoDataFrame`.

        Args:
            input_geodataframe: one or more `GeoDataFrame` with data to process.
            urban_layer: Urban layer for spatial context.

        Returns:
            GeoDataFrame: Data with imputed coordinates.

        Raises:
            ValueError: If inputs are None or columns are unset.

        Examples:
            >>> from urban_mapper.modules.imputer import AddressGeoImputer
            >>> from urban_mapper.modules.urban_layer import OSMNXStreets
            >>> imputer = AddressGeoImputer(
            ...     address_column="address",
            ...     latitude_column="lat",
            ...     longitude_column="lng"
            ... )
            >>> streets = OSMNXStreets().from_place("London, UK")
            >>> gdf = imputer.transform(data_gdf, streets)

        !!! note
            Ensure latitude_column and longitude_column are set before calling.
        """
        if isinstance(input_geodataframe, gpd.GeoDataFrame):
            return self._transform(input_geodataframe, urban_layer)
        else:
            return {
                key: self._transform(gdf, urban_layer)
                if self.data_id is None or self.data_id == key
                else gdf
                for key, gdf in input_geodataframe.items()
            }

    @abstractmethod
    def preview(self, format: str = "ascii") -> Any:
        """Generate a preview of the imputer's configuration.

        !!! note "To be implemented by subclasses"
            This method should provide a summary of the imputer's settings,
            including any parameters or configurations that are relevant to
            the imputation process.

        Args:
            format: Output format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            Any: Preview in specified format (e.g., str for "ascii", dict for "json").

        Raises:
            ValueError: If format is unsupported.

        !!! warning "Abstract Method"
            Subclasses must implement this method to provide configuration insights.
        """
        pass
