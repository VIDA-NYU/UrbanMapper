from typing import Optional, Union, Any
import geopandas as gpd
from beartype import beartype
from osmnx_mapping.modules.preprocessing import (
    CreatePreprocessor,
    GeoImputerBase,
    GeoFilterBase,
)
from osmnx_mapping.utils import (
    require_arguments_not_none,
    require_attributes_not_none,
    require_attribute_none,
)


class PreprocessingMixin:
    @beartype
    def __init__(
        self,
        preprocessor: Optional[Union[GeoImputerBase, GeoFilterBase]] = None,
    ) -> None:
        self.preprocessor_instance: Optional[Union[GeoImputerBase, GeoFilterBase]] = (
            preprocessor
        )

    @require_attribute_none(
        "preprocessor_instance",
        error_msg="A preprocessor is already set. Only one preprocessor type is allowed per instance.",
    )
    @beartype
    def with_imputer(
        self,
        imputer_type: str,
        latitude_column_name: str,
        longitude_column_name: str,
        **extra_params: Any,
    ) -> "PreprocessingMixin":
        self.preprocessor_instance = (
            CreatePreprocessor()
            .with_imputer(
                imputer_type=imputer_type,
                latitude_column_name=latitude_column_name,
                longitude_column_name=longitude_column_name,
                **extra_params,
            )
            .build()
        )
        return self

    @require_attribute_none(
        "preprocessor_instance",
        error_msg="A preprocessor is already set. Only one preprocessor type is allowed per instance.",
    )
    @beartype
    def with_default_imputer(
        self, latitude_column_name: str, longitude_column_name: str
    ) -> "PreprocessingMixin":
        self.preprocessor_instance = (
            CreatePreprocessor()
            .with_imputer(
                imputer_type="SimpleGeoImputer",
                latitude_column_name=latitude_column_name,
                longitude_column_name=longitude_column_name,
            )
            .build()
        )
        return self

    @require_attribute_none(
        "preprocessor_instance",
        error_msg="A preprocessor is already set. Only one preprocessor type is allowed per instance.",
    )
    @beartype
    def with_filter(
        self, filter_type: str, **extra_params: Any
    ) -> "PreprocessingMixin":
        self.preprocessor_instance = (
            CreatePreprocessor()
            .with_filter(filter_type=filter_type, **extra_params)
            .build()
        )
        return self

    @require_attribute_none(
        "preprocessor_instance",
        error_msg="A preprocessor is already set. Only one preprocessor type is allowed per instance.",
    )
    @beartype
    def with_default_filter(self, nodes: gpd.GeoDataFrame) -> "PreprocessingMixin":
        self.preprocessor_instance = (
            CreatePreprocessor()
            .with_filter(
                filter_type="BoundingBoxFilter",
                nodes=nodes,
            )
            .build()
        )
        return self

    @require_arguments_not_none("input_data", error_msg="Input data cannot be None.")
    @require_attributes_not_none(
        "preprocessor_instance",
        error_msg="No preprocessor set. Use with_imputer(), with_default_imputer(), with_filter(), or with_default_filter(), or pass a preprocessor to the constructor.",
    )
    @beartype
    def transform(
        self,
        input_data: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        return self.preprocessor_instance.transform(input_data)
