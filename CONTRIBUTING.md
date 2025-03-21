<div align="center">
   <h1>UrbanMapper</h1>
   <h3>Enrich Urban Layers Given Urban Datasets</h3>
   <p><i>with ease-of-use API and Sklearn-alike Shareable & Reproducible Urban Pipeline</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Beartype&message=compliant&color=4CAF50&style=for-the-badge&logo=https://avatars.githubusercontent.com/u/63089855?s=48&v=4&logoColor=white" alt="Beartype compliant">
      <img src="https://img.shields.io/static/v1?label=UV&message=compliant&color=2196F3&style=for-the-badge&logo=UV&logoColor=white" alt="UV compliant">
      <img src="https://img.shields.io/static/v1?label=RUFF&message=compliant&color=9C27B0&style=for-the-badge&logo=RUFF&logoColor=white" alt="RUFF compliant">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/static/v1?label=Python&message=3.9%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
   </p>
</div>

# Contributing to UrbanMapper

---

Welcome to the contributing guide for **UrbanMapper**! We’re excited to have you join us in enhancing this project. This
guide will help you set up your development environment, create new components, and submit your contributions. Whether
you’re fixing a bug, adding a feature, or improving documentation, your efforts make a big difference.

> [!IMPORTANT]  
> UrbanMapper is under active development, so expect frequent updates and changes. If you run into issues or have
> questions, feel free to open a GitHub Issue.

---

## 🛠️ Environment Setup

To contribute to UrbanMapper, you’ll need to set up your development environment. We recommend using `uv` for managing
dependencies due to its speed and simplicity, though other package managers like `pip` or `conda` can work too.

### Prerequisites

- **Install `uv`**: Follow the [official instructions](https://docs.astral.sh/uv/getting-started/installation/) to
  install `uv`.

### Steps to Set Up

1. **Clone the UrbanMapper repository**:
   ```bash
   git clone git@github.com:VIDA-NYU/UrbanMapper.git
   cd UrbanMapper
   ```

2. **Lock and sync dependencies with `uv`**:
   ```bash
   uv lock
   uv sync
   ```

3. **(Optional) Install Jupyter extensions** for interactive visualisations:
   ```bash
   uv run jupyter labextension install @jupyter-widgets/jupyterlab-manager
   ```

4. **Launch Jupyter Lab** to explore UrbanMapper:
   ```bash
   uv run --with jupyter jupyter lab
   ```

> [!NOTE]  
> If you prefer not to use `uv`, you can use `pip` or `conda`, but `uv` is our recommended tool for its performance
> benefits.

---

## 🧹 Linting and Formatting with Ruff

UrbanMapper uses `ruff` for linting and auto-formatting to keep our codebase consistent and clean. Before submitting
your changes, check your files with `ruff` to ensure they meet our style standards.

### Running Ruff

- **Check for linting issues**:
  ```bash
  uv run ruff check
  ```

- **Auto-fix formatting issues**:
  ```bash
  uv run ruff check --fix
  ```

> [!TIP]  
> Add `ruff` to your editor (e.g., VSCode) for real-time linting and formatting feedback.

---

## 🔒 Pre-Commit Hooks

To maintain consistent coding standards and avoid style-related comments during code reviews, we use pre-commit hooks.
These hooks automatically run checks (like `ruff`) before each commit.

### Setting Up Pre-Commit

1. **Install pre-commit**:
   ```bash
   uv run pre-commit install
   ```

2. **Run pre-commit manually** (optional, to test it):
   ```bash
   uv run pre-commit run --all-files
   ```

> [!IMPORTANT]  
> Once installed, pre-commit hooks run automatically on every `git commit`. If issues are detected, the commit will fail
> until they’re resolved.

---

## 🧩 How to Create New Components

UrbanMapper’s modular architecture makes it easy to extend with new components. Below are instructions for creating each
type, based on the existing codebase patterns.

### 📥 How to Create a New Loader

Loaders fetch data from various file formats (e.g., CSV, Parquet, Shapefiles) and return a `GeoDataFrame`.

1. **Subclass `LoaderBase`**:
    - Located in `urban_mapper/modules/loader/abc_loader.py`.
    - Implement the abstract method `load_data_from_file` to read your data source.

2. **Register the Loader**:
    - Add it to `FILE_LOADER_FACTORY` in `urban_mapper/modules/loader/loader_factory.py`

**Example** (from `csv_loader.py`):

```python
from urban_mapper.modules.loader.abc_loader import LoaderBase
import geopandas as gpd
import pandas as pd
from beartype import beartype


@beartype
class CSVLoader(LoaderBase):
    def load_data_from_file(self) -> gpd.GeoDataFrame:
        df = pd.read_csv(self.file_path)
        ...
```

- Place your new loader in `urban_mapper/modules/loader/loaders/`.
- Follow naming conventions like `csv_loader.py`.

---

### 🗺️ How to Create a New Urban Layer

Urban layers represent spatial entities (e.g., streets, sidewalks) as `GeoDataFrames`.

1. **Subclass `UrbanLayerBase`**:
    - Located in `urban_mapper/modules/urban_layer/abc_urban_layer.py`.
    - Implement methods like `from_place` or `from_file` to load the layer, and `_map_nearest_layer` to map data points.

**Example** (from `osmnx_streets.py`):

```python
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
import geopandas as gpd
import osmnx as ox
from beartype import beartype


@beartype
class OSMNXStreets(UrbanLayerBase):
    def from_place(self, place_name: str, **kwargs) -> None:
        self.network = StreetNetwork()
        self.network.load("place", query=place_name, undirected=True, **kwargs)
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.network.graph)
        self.layer = gdf_edges.to_crs(self.coordinate_reference_system)

    def _map_nearest_layer(self, data: gpd.GeoDataFrame, longitude_column: str, latitude_column: str,
                           output_column: str = "nearest_street", **kwargs):
        # Implementation for mapping nearest streets
        pass
```

- Add your urban layer to `urban_mapper/modules/urban_layer/urban_layers/`.
- Ensure it supports `get_layer` and optionally `static_render`.

> [!NOTE]  
> We automatically detect the urban layers available in /urban_mapper/modules/urban_layer/urban_layers/
> and make them available for use anywhere so no need to add them to the registry like the loaders.

---

### 🧩 How to Create a New Imputer

Imputers fill in missing geospatial data (e.g., coordinates) in datasets.

1. **Subclass `GeoImputerBase`**:
    - Located in `urban_mapper/modules/imputer/abc_imputer.py`.
    - Implement `_transform` to impute data and `preview` for configuration display.

**Example** (from `simple_geo_imputer.py`):

```python
from urban_mapper.modules.imputer.abc_imputer import GeoImputerBase
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
import geopandas as gpd
from beartype import beartype


@beartype  # Make sure to always use beartype for type checking
class SimpleGeoImputer(GeoImputerBase):
    def _transform(self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase) -> gpd.GeoDataFrame:
        # Simple imputation logic
        # You may or may not use the urban layer
        return input_geodataframe

    def preview(self, format: str = "ascii") -> str:
        # Recommend to implement a preview method to show configuration
        # Both on ascii (string) and json (dict) format
        return f"Imputer: SimpleGeoImputer\n  Lat: {self.latitude_column}\n  Lon: {self.longitude_column}"
```

- Place it in `urban_mapper/modules/imputer/imputers/`.

> [!NOTE]  
> We automatically detect the urban layers available in urban_mapper/modules/imputer/imputers
> and make them available for use anywhere so no need to add them to the registry like the loaders.

---

### 🧩 How to Create a New Filter

Filters refine datasets based on urban layer's spatial boundaries or other criteria.

1. **Subclass `GeoFilterBase`**:
    - Located in `urban_mapper/modules/filter/abc_filter.py`.
    - Implement `_transform` to filter data and `preview` for configuration.

**Example** (from `bounding_box_filter.py`):

```python
from urban_mapper.modules.filter.abc_filter import GeoFilterBase
from urban_mapper.modules.urban_layer.abc_urban_layer import UrbanLayerBase
import geopandas as gpd
from beartype import beartype


@beartype
class BoundingBoxFilter(GeoFilterBase):
    def _transform(self, input_geodataframe: gpd.GeoDataFrame, urban_layer: UrbanLayerBase) -> gpd.GeoDataFrame:
        minx, miny, maxx, maxy = urban_layer.get_layer_bounding_box()
        return input_geodataframe.cx[minx:maxx, miny:maxy]

    def preview(self, format: str = "ascii") -> str:
        # Recommend to implement a preview method to show configuration
        # Both on ascii (string) and json (dict) format
        return "Filter: BoundingBoxFilter\n  Action: Filter to urban layer bounding box"
```

- Add it to `urban_mapper/modules/filter/filters/`.

> [!NOTE]  
> We automatically detect the urban layers available in urban_mapper/modules/filter/filters/
> and make them available for use anywhere so no need to add them to the registry like the loaders.

---

### 🧩 How to Create a New Enricher / Aggregator

Enrichers and aggregators form a critical part of UrbanMapper, enabling the library to enhance urban layers with
summarised insights from datasets. This section explains how they work together, clarifies their current implementation,
and provides a step-by-step guide to extend them with new functionality.

#### What Are Enrichers and Aggregators?

**Enrichers** are the workhorses that take an urban layer (think of it as your city streets or sidewalks) and enrich it with new
data-driven insights. Want to know how many coffee shops are in each neighborhood or the average noise level per block?
That’s an enricher’s job. They process datasets and attach the results to the urban layer.

**Aggregators** are the helpers enrichers rely on to summarise raw data into meaningful stats. They group and crunch
numbers—like counting items, averaging values, or (as we’ll see) summing stuff up. For example, an enricher might use an
aggregator to count points within each feature of the urban layer or calculate totals based on some attribute.

Here’s the kicker: enrichers and aggregators don’t work in isolation. An enricher calls an aggregator to do the heavy
lifting on the data, then takes that summarised output and sticks it onto the urban layer. The `EnricherFactory` ties
them together, building enricher instances with the right aggregator based on a configuration.

#### How It Works Right Now

- **Enrichers**: These are plug-and-play. Drop a new enricher subclass into `urban_mapper/modules/enricher/enrichers/`,
  and UrbanMapper auto-detects it via a registry.
- **Aggregators**: Not so much. Unlike enrichers, aggregators aren’t auto-detected. The `EnricherFactory` (in
  `urban_mapper/modules/enricher/enricher_factory.py`) has a hardcoded list of supported aggregators tied to specific
  actions—like "aggregate" for `SimpleAggregator` or "count" for `CountAggregator`. Want a new aggregator? You’ll need
  to tweak the factory manually or open an issue for help on that end.

This difference matters. Enrichers are easy to extend, but aggregators require some code surgery. Let’s fix that
confusion and show you how to add a new aggregator—say, one that sums values.

#### Adding a New Aggregator: Step-by-Step

Note the following does not makes sense to add as `CountAggregator` does the same thing.

Let’s create a `SumAggregator` that totals up a column’s values grouped by another column (e.g., summing population per
district). Here’s how:

##### 1. **Create the Aggregator Class**

Subclass `BaseAggregator` (found in `urban_mapper/modules/enricher/aggregator/abc_aggregator.py`) and define how it
summarises data in the `_aggregate` method.

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
        grouped = input_dataframe.groupby(self.group_by_column)
        return grouped[self.value_column].sum()
```

- **`group_by_column`**: The column to group by (e.g., "district_id").
- **`value_column`**: The column to sum (e.g., "population").
- **`_aggregate`**: Groups the data and returns a pandas Series with sums.

Save this in `urban_mapper/modules/enricher/aggregator/aggregators/sum_aggregator.py`.

##### 2. **Hook It Into `EnricherFactory`**

Open `urban_mapper/modules/enricher/enricher_factory.py` and update the `build` method to recognise a new "sum" action.

```python
def build(self) -> EnricherBase:
    validate_group_by(self.config)
    validate_action(self.config)

    if self.config.action == "aggregate":
        validate_aggregation_method(self.config.aggregator_config["method"])
        aggregator = SimpleAggregator(
            group_by_column=self.config.group_by[0],
            value_column=self.config.values_from[0],
            aggregation_function=AGGREGATION_FUNCTIONS[self.config.aggregator_config["method"]],
        )
    elif self.config.action == "count":
        aggregator = CountAggregator(
            group_by_column=self.config.group_by[0],
            count_function=len,
        )
    elif self.config.action == "sum":
        if not self.config.values_from:
            raise ValueError("Sum aggregation requires 'values_from'")
        aggregator = SumAggregator(
            group_by_column=self.config.group_by[0],
            value_column=self.config.values_from[0],
        )
    else:
        raise ValueError(f"Unknown action '{self.config.action}'.")

    enricher_class = ENRICHER_REGISTRY[self.config.enricher_type]
    self._instance = enricher_class(
        aggregator=aggregator,
        output_column=self.config.enricher_config["output_column"],
        config=self.config,
    )
    return self._instance
```

- **New bit**: The `elif self.config.action == "sum"` block creates a `SumAggregator` when the config specifies "sum".
- **Validation**: It checks that `values_from` is set, since summing needs a column to work with.

Note that at some points we'll have to generalise this to avoid a forest of `if` statements.

##### 3. **Add a Configuration Shortcut**

In `urban_mapper/modules/enricher/factory/config.py`, add a `sum_by` method to `EnricherConfig` so users can easily
configure this action.

```python
def sum_by(self, output_column: str = None) -> "EnricherConfig":
    if not self.values_from:
        raise ValueError("Sum aggregation requires 'values_from'")
    self.action = "sum"
    self.aggregator_config = {}
    self.enricher_config = {"output_column": output_column or f"sum_{self.values_from[0]}"}
    return self
```

- **`output_column`**: Where the summed results go (defaults to something like "sum_population").
- **Chaining**: Fits into the fluent API (e.g., `.with_data().sum_by()`).

##### 4. **Use It in an Enricher**

Now you can build an enricher with your new aggregator:

```python
enricher = [...].with_data(group_by="district_id", values_from="population").sum_by().build()
```

This sums the "population" column per "district_id" and adds the result to the urban layer.

#### Key Notes

- **Enrichers Are Easy**: Just subclass and drop them in the directory—UrbanMapper finds them automatically.
- **Aggregators Are Manual**: You’ve got to update `EnricherFactory` for each new one. It’s a limitation, not a feature.

---

### 🧩 How to Create a New Visualiser

Visualisers render urban layers and enriched data on maps.

1. **Subclass `VisualiserBase`**:
    - Located in `urban_mapper/modules/visualiser/abc_visualiser.py`.
    - Implement `_render` to display the data and `preview` for configuration.

**Example** (from `static_visualiser.py`):

```python
from urban_mapper.modules.visualiser.abc_visualiser import VisualiserBase
from typing import List
import geopandas as gpd
from beartype import beartype


@beartype
class StaticVisualiser(VisualiserBase):
    short_name = "Static"  # Name used in with_type() method
    allowed_style_keys = {"cmap", "color", "legend", "figsize"}  # Allowed style keys in with_style() method

    def _render(self, urban_layer_geodataframe: gpd.GeoDataFrame, columns: List[str], **kwargs):
        ax = urban_layer_geodataframe.plot(column=columns[0], legend=True, **kwargs)
        return ax.get_figure()

    def preview(self, format: str = "ascii") -> str:
        # Recommend to implement a preview method to show configuration
        # Both on ascii (string) and json (dict) format
        return "Visualiser: StaticVisualiser using Matplotlib"
```

- Add it to `urban_mapper/modules/visualiser/visualisers/`.

> [!NOTE]
> We automatically detect the visualisers available in urban_mapper/modules/visualiser/visualisers/
> and make them available for use anywhere so no need to add them to the registry like the loaders.

---

## 📬 Pull Requests and Rebasing

When submitting your contributions, follow these steps to ensure a smooth review process:

1. **Create a Feature Branch**:
    - Start a new branch for your work:
      ```bash
      git checkout -b feature/your-feature-name # We use Git Karma Convention for commit messages and branch naming.
      ```

2. **Commit Meaningfully**:
    - Use clear, descriptive commit messages (e.g., “Add CSVLoader for CSV files”). <--- Use Git Karma Convention for
      commit messages.
    - Avoid auto-squashing; we preserve commit history for better traceability.

3. **Rebase Before Pushing**:
    - Keep your branch up-to-date with `main` and maintain a linear history:
      ```bash
      git fetch origin
      git rebase origin/main
      ```

4. **Submit a Pull Request**:
    - Push your branch to GitHub and open a PR against `main`.
    - Include a description linking to any related issues.

5. **Address Feedback**:
    - Respond to review comments and update your PR as needed.

> [!TIP]  
> Use `git rebase -i` to refine your commit history before submitting, but avoid rewriting history on shared branches.

---

## 🎉 Thank You!

Thank you for contributing to UrbanMapper! Your work helps make urban data analysis more accessible and impactful.
If you have questions or need help, don’t hesitate to open an issue or contact the maintainers.

Happy mapping! 🌍