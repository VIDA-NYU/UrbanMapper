from typing import Any

import geopandas as gpd
from beartype import beartype
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
from urban_mapper.modules.imputer.abc_imputer import GeoImputerBase


@beartype
class SimpleGeoImputer(GeoImputerBase):
    """Imputer that removes (naively) rows with missing coordinates.

    Filters out rows with `NaN` in `latitude` or `longitude` columns, cleaning data for
    spatial operations.

    Attributes:
        latitude_column (str): Column with latitude values.
        longitude_column (str): Column with longitude values.

    Examples:
        >>> from urban_mapper.modules.imputer import SimpleGeoImputer
        >>> imputer = SimpleGeoImputer(latitude_column="lat", longitude_column="lng")
        >>> clean_gdf = imputer.transform(data_gdf, urban_layer)

    !!! note
        This imputer does not add coordinates; it only removes incomplete rows.
    """

    def _transform(
        self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase
    ) -> gpd.GeoDataFrame:
        """Filter rows with missing coordinates.

        Args:
            input_geodataframe: `GeoDataFrame` to clean.
            urban_layer: `Urban layer` (unused in this implementation).

        Returns:
            GeoDataFrame: Cleaned data without missing coordinates.

        !!! tip
            Use this as a preprocessing step before spatial analysis.
        """
        _ = urban_layer  # Not used in this implementation
        return input_geodataframe.dropna(
            subset=[self.latitude_column, self.longitude_column]
        )

    def preview(self, format: str = "ascii") -> Any:
        """Preview the imputer configuration.

        Args:
            format: Output format ("ascii" or "json"). Defaults to "ascii".

        Returns:
            Any: Configuration summary.

        Raises:
            ValueError: If format is unsupported.
        """
        if format == "ascii":
            lines = [
                f"Imputer: SimpleGeoImputer",
                f"  Action: Drop rows with missing '{self.latitude_column}' or '{self.longitude_column}'",
            ]
            if self.data_id:
                lines.append(f"  Data ID: '{self.data_id}'")

            return "\n".join(lines)
        elif format == "json":
            return {
                "imputer": "SimpleGeoImputer",
                "action": f"Drop rows with missing '{self.latitude_column}' or '{self.longitude_column}'",
                "latitude_column": self.latitude_column,
                "longitude_column": self.longitude_column,
                "data_id": self.data_id,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
