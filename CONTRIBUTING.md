<div align="center">
   <h1>UrbanMapper</h1>
   <h3>Enrich Urban Layers Given Urban Datasets</h3>
   <p><i>With an Easy-to-Use API and Sklearn-Alike Shareable & Reproducible Urban Pipeline</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Beartype&message=compliant&color=4CAF50&style=for-the-badge&logo=https://avatars.githubusercontent.com/u/63089855?s=48&v=4&logoColor=white" alt="Beartype compliant">
      <img src="https://img.shields.io/static/v1?label=UV&message=compliant&color=2196F3&style=for-the-badge&logo=UV&logoColor=white" alt="UV compliant">
      <img src="https://img.shields.io/static/v1?label=RUFF&message=compliant&color=9C27B0&style=for-the-badge&logo=RUFF&logoColor=white" alt="RUFF compliant">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
      <img src="https://img.shields.io/github/actions/workflow/status/VIDA-NYU/UrbanMapper/compile.yaml?style=for-the-badge&label=Compilation&logo=githubactions&logoColor=white" alt="Compilation Status">
   </p>
</div>

# Contributing to UrbanMapper

---

Welcome to the contributing guide for **UrbanMapper**! We're thrilled to have you join us in building a tool that makes urban data analysis accessible and powerful. This guide will walk you through setting up your environment, adding new components, and submitting your contributions. Whether you're fixing bugs, adding features, or improving docs, your work matters!

> **Important**: UrbanMapper is actively evolving. Expect changes, and if you hit a snag, open a GitHub Issue—we’re here to help!

---

## 🛠️ Environment Setup

Get started by setting up your development environment. We recommend `uv` for its speed, but `pip` or `conda` work too.

### Prerequisites
- **Install `uv`**: Grab it from the [official guide](https://docs.astral.sh/uv/getting-started/installation/).

### Steps
1. **Clone the Repo**:
   ```bash
   git clone git@github.com:VIDA-NYU/UrbanMapper.git
   cd UrbanMapper
   ```

2. **Sync Dependencies**:
   ```bash
   uv lock
   uv sync
   ```

3. **(Optional) Add Jupyter Extensions** for visualizations:
   ```bash
   uv run jupyter labextension install @jupyter-widgets/jupyterlab-manager
   ```

4. **Launch Jupyter Lab**:
   ```bash
   uv run --with jupyter jupyter lab
   ```

- **Config Note**: Check out `config.yaml` in `urban_mapper/` for pipeline schemas and mixin mappings. It’s optional for basic setup but key for advanced tweaks.

> **Tip**: Prefer `pip` or `conda`? That’s fine—just note `uv` is our go-to for performance.

---

## 🧹 Linting and Formatting with Ruff

We use `ruff` to keep the codebase clean and consistent. Run it before submitting changes.

### Commands
- **Check Issues**:
  ```bash
  uv run ruff check
  ```
- **Fix Formatting**:
  ```bash
  uv run ruff check --fix
  ```

> **Pro Tip**: Integrate `ruff` into your editor (e.g., VSCode) for live feedback.

---

## 🔒 Pre-Commit Hooks

Pre-commit hooks enforce standards by running checks (like `ruff`) before commits.

### Setup
1. **Install**:
   ```bash
   uv run pre-commit install
   ```
2. **Test Manually** (optional):
   ```bash
   uv run pre-commit run --all-files
   ```

> **Heads-Up**: Hooks run automatically on `git commit`. Fix any failures to proceed.

---

## 🧩 How to Create New Components

UrbanMapper’s modular design makes extending it a breeze. Here’s how to add each component type.

### 📥 New Loader
Loaders pull data (e.g., CSV, Shapefiles) into a `GeoDataFrame`.

1. **Subclass `LoaderBase`** (`urban_mapper/modules/loader/abc_loader.py`):
   - Implement `load_data_from_file`.
2. **Register It**:
   - Add to `FILE_LOADER_FACTORY` in `urban_mapper/modules/loader/loader_factory.py`.

**Example** (`csv_loader.py`):
```python
from urban_mapper.modules.loader.abc_loader import LoaderBase
import geopandas as gpd
import pandas as pd
from beartype import beartype

@beartype
class CSVLoader(LoaderBase):
    def load_data_from_file(self) -> gpd.GeoDataFrame:
        df = pd.read_csv(self.file_path)
        # Convert to GeoDataFrame...
        return gdf
```
- Place in `urban_mapper/modules/loader/loaders/`.

---

### 🗺️ New Urban Layer
Urban layers (e.g., streets) are spatial entities as `GeoDataFrames`.

1. **Subclass `UrbanLayerBase`** (`urban_mapper/modules/urban_layer/abc_urban_layer.py`):
   - Add methods like `from_place` or `_map_nearest_layer`.

**Example** (`osmnx_streets.py`):
```python
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
import geopandas as gpd
import osmnx as ox
from beartype import beartype

@beartype
class OSMNXStreets(UrbanLayerBase):
    def from_place(self, place_name: str, **kwargs) -> None:
        self.network = ox.graph_from_place(place_name, network_type="all")
        self.layer = ox.graph_to_gdfs(self.network)[1].to_crs(self.coordinate_reference_system)
```
- Place in `urban_mapper/modules/urban_layer/urban_layers/`.
- Auto-detected—no registration needed.

---

### 🧩 New Imputer
Imputers fill missing geospatial data.

1. **Subclass `GeoImputerBase`** (`urban_mapper/modules/imputer/abc_imputer.py`):
   - Implement `_transform` and `preview`.

**Example** (`simple_geo_imputer.py`):
```python
from urban_mapper.modules.imputer.abc_imputer import GeoImputerBase
import geopandas as gpd
from beartype import beartype

@beartype
class SimpleGeoImputer(GeoImputerBase):
    def _transform(self, input_geodataframe: gpd.GeoDataFrame, urban_layer) -> gpd.GeoDataFrame:
        # Impute logic here
        return input_geodataframe
    def preview(self, format: str = "ascii") -> str:
        return f"Imputer: SimpleGeoImputer\n  Lat: {self.latitude_column}"
```
- Place in `urban_mapper/modules/imputer/imputers/`.
- Auto-detected.

---

### 🧩 New Filter
Filters refine datasets (e.g., by spatial bounds).

1. **Subclass `GeoFilterBase`** (`urban_mapper/modules/filter/abc_filter.py`):
   - Implement `_transform`.

**Example** (`bounding_box_filter.py`):
```python
from urban_mapper.modules.filter.abc_filter import GeoFilterBase
import geopandas as gpd
from beartype import beartype

@beartype
class BoundingBoxFilter(GeoFilterBase):
    def _transform(self, input_geodataframe: gpd.GeoDataFrame, urban_layer) -> gpd.GeoDataFrame:
        minx, miny, maxx, maxy = urban_layer.get_layer_bounding_box()
        return input_geodataframe.cx[minx:maxx, miny:maxy]
```
- Place in `urban_mapper/modules/filter/filters/`.
- Auto-detected.

---

### 🧩 New Enricher / Aggregator
Enrichers enhance urban layers with insights; aggregators summarize data.

#### Enrichers
- **Subclass `EnricherBase`** (`urban_mapper/modules/enricher/abc_enricher.py`).
- Place in `urban_mapper/modules/enricher/enrichers/`.
- Auto-detected.

#### Aggregators
- **Subclass `BaseAggregator`** (`urban_mapper/modules/enricher/aggregator/abc_aggregator.py`).
- Update `EnricherFactory.build()` in `urban_mapper/modules/enricher/enricher_factory.py`.

**Example** (`sum_aggregator.py`):
```python
from urban_mapper.modules.enricher.aggregator.abc_aggregator import BaseAggregator
import pandas as pd
from beartype import beartype

@beartype
class SumAggregator(BaseAggregator):
    def __init__(self, group_by_column: str, value_column: str):
        self.group_by_column = group_by_column
        self.value_column = value_column
    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series:
        return input_dataframe.groupby(self.group_by_column)[self.value_column].sum()
```
- Place in `urban_mapper/modules/enricher/aggregator/aggregators/`.
- Add to `EnricherFactory`:
  ```python
  elif self.config.action == "sum":
      aggregator = SumAggregator(self.config.group_by[0], self.config.values_from[0])
  ```

---

### 🧩 New Visualizer
Visualizers render maps.

1. **Subclass `VisualizerBase`** (`urban_mapper/modules/visualiser/abc_visualiser.py`):
   - Implement `_render`.

**Example** (`static_visualiser.py`):
```python
from urban_mapper.modules.visualiser.abc_visualiser import VisualiserBase
import geopandas as gpd
from beartype import beartype

@beartype
class StaticVisualiser(VisualiserBase):
    def _render(self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: list, **kwargs):
        return urban_layer_geodataframe.plot(column=columns[0], legend=True, **kwargs).get_figure()
```
- Place in `urban_mapper/modules/visualiser/visualisers/`.
- Auto-detected.

---

### 🧩 New Pipeline Generator
Generators create pipeline steps dynamically.

1. **Subclass `PipelineGeneratorBase`** (`urban_mapper/modules/pipeline_generator/abc_pipeline_generator.py`).

**Example** (`gpt4o_pipeline_generator.py`):
```python
from urban_mapper.modules.pipeline_generator.abc_pipeline_generator import PipelineGeneratorBase
from beartype import beartype

@beartype
class GPT4OPipelineGenerator(PipelineGeneratorBase):
    def generate_pipeline(self, data_description: str) -> list:
        # AI-driven step generation
        return []
```
- Place in `urban_mapper/modules/pipeline_generator/generators/`.
- Auto-detected via `pipeline_generator_factory.py`.

---

## 🏗️ Pipeline Architecture

UrbanMapper’s pipeline flows like this:
1. **Loader**: Loads data.
2. **Imputers**: Fills gaps.
3. **Filters**: Refines data.
4. **Urban Layer**: Maps to spatial features.
5. **Enrichers**: Adds insights.
6. **Visualizer**: Shows results.

New components should slot into this sequence (see `urban_mapper/pipeline/`).

---

## 📊 Jupyter GIS Integration

Export pipelines to Jupyter GIS with `UrbanPipeline.to_jgis()` for interactive maps. Check `mixins/jupyter_gis.py` for details.

---

## 📬 Pull Requests and Rebasing

1. **Branch**:
   ```bash
   git checkout -b feat/your-feature
   ```
2. **Commit**:
   - Use Git Karma style (e.g., `feat: add new loader`).
3. **Rebase**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
4. **Submit PR**:
   - Push and open a PR against `main`.
- **Note**: We suggest [Git Karma](https://example.com/git-karma) for commits/branches (e.g., `feat/add-loader`), but it’s optional unless CI enforces it.

> **Tip**: Use `git rebase -i` to polish commits, but don’t rewrite shared history.

---

## 🎉 Thank You!

Thanks for contributing to UrbanMapper! Your efforts shape urban data analysis. Questions? Open an issue—we’ve got your back.

Happy mapping! 🌍