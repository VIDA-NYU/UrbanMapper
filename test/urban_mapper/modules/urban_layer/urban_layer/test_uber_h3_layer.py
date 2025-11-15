from __future__ import annotations

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

pytest.importorskip("h3")

from urban_mapper.modules.enricher.aggregator.aggregators.simple_aggregator import (
    SimpleAggregator,
)
from urban_mapper.modules.enricher.enrichers.single_aggregator_enricher import (
    SingleAggregatorEnricher,
)
from urban_mapper.modules.enricher.factory.config import EnricherConfig
from urban_mapper.modules.urban_layer.urban_layers.uber_h3 import UberH3Grid


BROOKLYN_BBOX = (-73.99, 40.67, -73.95, 40.70)


def _build_layer_from_bbox(resolution: int = 9) -> UberH3Grid:
    return UberH3Grid().from_bbox(list(BROOKLYN_BBOX), resolution=resolution)


def _stub_geocoder(geometry) -> object:
    class _Location:
        def __init__(self, geometry):
            self.raw = {"geojson": geometry}

    return _Location(geometry)


def test_from_bbox_builds_layer() -> None:
    layer = _build_layer_from_bbox(resolution=9)
    gdf = layer.get_layer()

    assert not gdf.empty
    assert layer.resolution == 9
    assert gdf.crs.to_string().upper() == "EPSG:4326"


def test_from_place_uses_geocoder(monkeypatch: pytest.MonkeyPatch) -> None:
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [-73.99, 40.67],
                [-73.95, 40.67],
                [-73.95, 40.70],
                [-73.99, 40.70],
                [-73.99, 40.67],
            ]
        ],
    }

    def _fake_geocode(*_, **__):
        return _stub_geocoder(geometry)

    layer = UberH3Grid()
    monkeypatch.setattr(
        layer, "_get_geolocator", lambda: type("Geo", (), {"geocode": _fake_geocode})()
    )

    layer.from_place("Brooklyn", resolution=8)

    assert layer.config is not None
    assert layer.config.source == "place"
    assert layer.config.metadata["place"] == "Brooklyn"


def test_from_address_requires_positive_distance() -> None:
    layer = UberH3Grid()

    with pytest.raises(ValueError):
        layer.from_address("Brooklyn", dist=0)


def test_from_point_requires_positive_distance() -> None:
    layer = UberH3Grid()

    with pytest.raises(ValueError):
        layer.from_point((40.0, -73.0), dist=0)


def test_from_bbox_records_configuration() -> None:
    layer = _build_layer_from_bbox(resolution=8)

    assert layer.config is not None
    assert layer.config.source == "bbox"
    assert layer.config.metadata["bbox"] == list(BROOKLYN_BBOX)


def test_map_nearest_layer_assigns_cell() -> None:
    layer = _build_layer_from_bbox(resolution=8)

    inside_point = Point(-73.97, 40.685)
    outside_point = Point(-73.90, 40.60)

    points = gpd.GeoDataFrame(
        {"name": ["inside", "outside"]},
        geometry=[inside_point, outside_point],
        crs="EPSG:4326",
    )

    _, mapped = layer.map_nearest_layer(
        data=points,
        geometry_column="geometry",
        output_column="h3_cell",
    )

    assert mapped.loc[mapped["name"] == "inside", "h3_cell"].notna().all()
    assert mapped.loc[mapped["name"] == "outside", "h3_cell"].isna().all()


def test_map_nearest_layer_threshold_distance_filters() -> None:
    layer = _build_layer_from_bbox(resolution=8)

    df = pd.DataFrame(
        {
            "longitude": [-73.97, -73.97],
            "latitude": [40.685, 40.71],
        }
    )
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    )

    _, mapped = layer.map_nearest_layer(
        data=gdf,
        longitude_column="longitude",
        latitude_column="latitude",
        output_column="h3_cell",
        threshold_distance=500,
        distance_crs="EPSG:3857",
    )

    assert mapped.loc[mapped["latitude"] == 40.685, "h3_cell"].notna().all()
    assert mapped.loc[mapped["latitude"] == 40.71, "h3_cell"].isna().all()


def test_map_nearest_layer_ignores_invalid_coordinates() -> None:
    layer = _build_layer_from_bbox(resolution=8)

    df = pd.DataFrame(
        {
            "longitude": [-73.97, -181.0],
            "latitude": [40.685, 95.0],
        }
    )
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    )

    _, mapped = layer.map_nearest_layer(
        data=gdf,
        longitude_column="longitude",
        latitude_column="latitude",
        output_column="h3_cell",
    )

    assert mapped.loc[mapped["latitude"] == 40.685, "h3_cell"].notna().all()
    assert mapped.loc[mapped["latitude"] == 95.0, "h3_cell"].isna().all()


def test_preview_formats() -> None:
    layer = _build_layer_from_bbox(resolution=7)
    layer_preview = layer.preview()
    layer_preview_json = layer.preview(format="json")

    assert "UberH3Grid" in layer_preview
    assert layer_preview_json["urban_layer"] == "UberH3Grid"
    assert layer_preview_json["resolution"] == 7


def test_enrichment_populates_values() -> None:
    layer = _build_layer_from_bbox(resolution=8)

    points = gpd.GeoDataFrame(
        {
            "numfloors": [10.0, 20.0],
        },
        geometry=[
            Point(-73.97, 40.685),
            Point(-73.969, 40.686),
        ],
        crs="EPSG:4326",
    )

    _, mapped = layer.map_nearest_layer(
        data=points,
        geometry_column="geometry",
        output_column="h3_cell",
    )

    aggregator = SimpleAggregator(
        group_by_column="h3_cell",
        value_column="numfloors",
        aggregation_function=pd.Series.mean,
    )
    enricher = SingleAggregatorEnricher(
        aggregator=aggregator,
        output_column="avg_floors",
        config=EnricherConfig(),
    )

    enriched_layer = enricher.enrich(mapped, layer)
    result = enriched_layer.get_layer()

    first_cell = mapped.loc[0, "h3_cell"]
    expected_mean = mapped.loc[mapped["h3_cell"] == first_cell, "numfloors"].mean()

    assert result["avg_floors"].max() > 0
    assert result.loc[first_cell, "avg_floors"] == pytest.approx(expected_mean)
    assert result.index.name is None
