import geopandas as gpd
from pathlib import Path
from typing import Tuple, Any
from beartype import beartype

from urban_mapper.utils import require_attributes_not_none
from ..abc_urban_layer import UrbanLayerBase


@beartype
class Tile2NetCrosswalks(UrbanLayerBase):
    def from_file(self, file_path: str | Path, **kwargs) -> None:
        self.layer = gpd.read_file(file_path)
        self.layer = self.layer[self.layer["f_type"] == "crosswalk"]
        self.layer = self.layer.to_crs(self.coordinate_reference_system)
        if "feature_id" in self.layer.columns:
            raise ValueError(
                "Feature ID column already exists in the layer. Please remove it before loading."
            )
        self.layer["feature_id"] = self.layer.index

    def from_place(self, place_name: str, **kwargs) -> None:
        raise NotImplementedError(
            "Loading crosswalks from place is not yet implemented."
        )

    @require_attributes_not_none(
        "layer", error_msg="Layer not loaded. Call from_file() first."
    )
    def _map_nearest_layer(
        self,
        data: gpd.GeoDataFrame,
        longitude_column: str,
        latitude_column: str,
        output_column: str = "nearest_crosswalk",
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
            layer_projected[["geometry", "feature_id"]],
            how="left",
            max_distance=threshold_distance,
            distance_col="distance_to_crosswalk",
        )
        mapped_data[output_column] = mapped_data["feature_id"]
        return self.layer, mapped_data.drop(
            columns=["feature_id", "distance_to_crosswalk", "index_right"]
        )

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_file() first."
    )
    def get_layer(self) -> gpd.GeoDataFrame:
        return self.layer

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_file() first."
    )
    def get_layer_bounding_box(self) -> Tuple[float, float, float, float]:
        return tuple(self.layer.total_bounds)  # type: ignore

    @require_attributes_not_none(
        "layer", error_msg="Layer not built. Call from_file() first."
    )
    def static_render(self, **plot_kwargs) -> None:
        self.layer.plot(**plot_kwargs)

    def preview(self, format: str = "ascii") -> Any:
        mappings_str = (
            "\n".join(
                "Mapping:\n"
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
                f"Urban Layer: Tile2NetCrosswalks\n"
                f"  CRS: {self.coordinate_reference_system}\n"
                f"  Mappings:\n{mappings_str}"
            )
        elif format == "json":
            return {
                "urban_layer": "Tile2NetCrosswalks",
                "coordinate_reference_system": self.coordinate_reference_system,
                "mappings": self.mappings,
            }
        else:
            raise ValueError(f"Unsupported format '{format}'")
