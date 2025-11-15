from __future__ import annotations

import geopandas as gpd
import ipywidgets as widgets
import pandas as pd
import pytest
from lonboard import Map
from shapely.geometry import Point, Polygon

from urban_mapper.modules.visualiser.visualisers.interactive_visualiser import (
    InteractiveVisualiser,
)
from urban_mapper.modules.visualiser.visualisers.static_visualiser import (
    StaticVisualiser,
)
from urban_mapper.modules.visualiser.visualisers.lonboard.classic import (
    LonboardClassicVisualiser,
)
from urban_mapper.modules.visualiser.visualisers.lonboard.heatmap import (
    LonboardHeatmapVisualiser,
)


@pytest.fixture()
def sample_point_gdf() -> gpd.GeoDataFrame:
    df = pd.DataFrame(
        {
            "value": [1, 2, 3],
            "category": ["a", "b", "c"],
            "geometry": [Point(0, 0), Point(1, 1), Point(2, 2)],
        }
    )
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")


@pytest.fixture()
def sample_polygon_gdf() -> gpd.GeoDataFrame:
    polygons = [
        Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
        Polygon([(1, 1), (1, 2), (2, 2), (2, 1)]),
        Polygon([(2, 2), (2, 3), (3, 3), (3, 2)]),
    ]
    df = pd.DataFrame({"value": [10, 20, 30], "geometry": polygons})
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")


def test_static_visualiser_renders_single_column(sample_polygon_gdf: gpd.GeoDataFrame) -> None:
    visualiser = StaticVisualiser()
    figure = visualiser.render(sample_polygon_gdf, ["value"])
    assert figure is not None
    assert figure.axes, "Expected at least one axis in the generated figure."


def test_interactive_visualiser_handles_multiple_columns(sample_point_gdf: gpd.GeoDataFrame) -> None:
    visualiser = InteractiveVisualiser()
    widget = visualiser.render(sample_point_gdf, ["value", "category"])
    assert isinstance(widget, widgets.VBox)
    assert len(widget.children) == 2, "Dropdown and output widgets should be returned."


def test_lonboard_classic_visualiser_creates_map(sample_polygon_gdf: gpd.GeoDataFrame) -> None:
    visualiser = LonboardClassicVisualiser()
    result = visualiser.render(sample_polygon_gdf, ["value"])
    assert isinstance(result, Map)


def test_lonboard_heatmap_visualiser_creates_map(sample_point_gdf: gpd.GeoDataFrame) -> None:
    visualiser = LonboardHeatmapVisualiser()
    result = visualiser.render(sample_point_gdf, ["value"])
    assert isinstance(result, Map)
