import geopandas as gpd
from pathlib import Path
from typing import Tuple, Any
from beartype import beartype

from urban_mapper.config import DEFAULT_CRS
from ..abc_urban_layer import UrbanLayerBase
from urban_mapper.utils import require_attributes_not_none


@beartype
class CustomUrbanLayer(UrbanLayerBase):
    def __init__(self) -> None:
        super().__init__()
        self.source: str | None = None

    def from_file(self, file_path: str | Path, **kwargs) -> None:
        if not (str(file_path).endswith(".shp") or str(file_path).endswith(".geojson")):
            raise ValueError(
                "Only shapefiles (.shp) and GeoJSON (.geojson) are supported for loading from file."
            )

        self.layer = gpd.read_file(file_path)
        if self.layer.crs is None:
            self.layer.set_crs(DEFAULT_CRS, inplace=True)
        else:
            self.layer = self.layer.to_crs(DEFAULT_CRS)

        if "geometry" not in self.layer.columns:
            raise ValueError("The loaded file does not contain a geometry column.")

        self.source = "file"

    def from_urban_layer(self, urban_layer: UrbanLayerBase, **kwargs) -> None:
        if not isinstance(urban_layer, UrbanLayerBase):
            raise ValueError(
                "The provided object is not an instance of UrbanLayerBase."
            )
        if urban_layer.layer is None:
            raise ValueError(
                "The provided urban layer has no data. Ensure it has been enriched or loaded."
            )

        self.layer = urban_layer.get_layer().copy()
        self.source = "urban_layer"

    def from_place(self, place_name: str, **kwargs) -> None:
        raise NotImplementedError(
            "Loading from place is not supported for CustomUrbanLayer."
        )

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not loaded. Call from_file() or from_urban_layer() first.",
    )
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_feature",
        threshold_distance: float | None = None,
        _reset_layer_index: bool = True,
        **kwargs,
    ) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        dataframe = data.copy()

        if "geometry" not in dataframe.columns:
            dataframe = gpd.GeoDataFrame(
                dataframe,
                geometry=gpd.points_from_xy(
                    dataframe[longitude_column], dataframe[latitude_column]
                ),
                crs=self.coordinate_reference_system,
            )

        if not dataframe.crs.is_projected:
            utm_crs = dataframe.estimate_utm_crs()
            dataframe = dataframe.to_crs(utm_crs)
            layer_projected = self.layer.to_crs(utm_crs)
        else:
            layer_projected = self.layer

        mapped_data = gpd.sjoin_nearest(
            dataframe,
            layer_projected[["geometry"]],
            how="left",
            max_distance=threshold_distance,
            distance_col="distance_to_feature",
        )
        mapped_data[output_column] = mapped_data.index_right

        if mapped_data.index.duplicated().any():
            mapped_data = mapped_data.reset_index(drop=True)

        if _reset_layer_index:
            self.layer = self.layer.reset_index()

        return self.layer, mapped_data.drop(
            columns=["distance_to_feature", "index_right"], errors="ignore"
        )

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call from_file() or from_urban_layer() first.",
    )
    def get_layer(self) -> gpd.GeoDataFrame:
        return self.layer

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call from_file() or from_urban_layer() first.",
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "layer",
        error_msg="Layer not built. Call from_file() or from_urban_layer() first.",
    )
    def static_render(self, **plot_kwargs) -> None:
        self.layer.plot(**plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        mappings_str = (
            "\n".join(
                f"    - lon={m.get('longitude_column', 'N/A')}, "
                f"lat={m.get('latitude_column', 'N/A')}, "
                f"output={m.get('output_column', 'N/A')}"
                for m in self.mappings
            )
            if self.mappings
            else "    No mappings"
        )
        if format == "ascii":
            return (
                f"Urban Layer: CustomUrbanLayer\n"
                f"  Source: {self.source or 'Not loaded'}\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": "CustomUrbanLayer",
                "source": self.source or "Not loaded",
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
