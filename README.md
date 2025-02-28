<div align="center">
   <h1>OSMNxMapping</h1>
   <h3>Mapping Urban Data to Street Networks</h3>
    <p><i>with ease-of-use</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Python&message=3.9%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
      <img src="https://img.shields.io/badge/OSMNx-4CAF50?style=for-the-badge&logo=openstreetmap&logoColor=white" alt="OSMNx">
      <img src="https://img.shields.io/badge/Skrub-FF9800?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Skrub">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/badge/RUFF-9C27B0?style=for-the-badge" alt="RUFF">
      <img src="https://img.shields.io/badge/UV-2196F3?style=for-the-badge" alt="UV">
      <img src="https://img.shields.io/badge/Version-0.1.0-red?style=for-the-badge" alt="Version">
      <img src="https://img.shields.io/badge/status-unstable-orange?style=for-the-badge" alt="Unstable">
   </p>
   <p>Map your urban dataset with the street network of your choice, urban pipeline your analysis, and propagate it along the <i>urban research network</i>!</p>
</div>

---

![OSMNxMapping Cover](public/resources/osmnx_mapping_cover.png)

> [!IMPORTANT]
> 1) We highly recommend to explore the `/example` folder for Jupyter Notebook-based tutorials 🎉
> 2) The following library is under active-development and is not yet _stable_. Expect bugs & frequent changes!

## 🌆 OSMNxMapping –– In a Nutshell

`OSMNxMapping` –– `f(.)` –– brings road networks from OpenStreetMap –– `X` –– and your urban datasets –– `Y` –– together
through the function *f(X, Y) = X ⋈ Y*, allowing you to map these components in any direction—whether attaching the
streets based on your dataset’s `latitude` and `longitude` coordinates, or computing **insights** from your _datasets_
to
attach to the _street network_.

`OSMNxMapping`, built with a **Scikit-Learn-like philosophy** – i.e., (I) from `loading` to `viz.` passing by `mapping`,
we want to cover as much as users’ wishes in a welcoming way without having to code 20+/50+ lines of code for one,
~~non-reproducible, non-shareable, non-updatable piece of code;~~ and (II) the library’s flexibility allows for easy
contributions to sub-modules without having to start from scratch _“all the time”_.


<details>
<summary><strong> 👀Read me! Click here ⬅️</strong></summary>

To answer (I) –– one out many other ways –– we propose a `scikit-like` pipeline to, for instance, stack the following
steps:

1) Query a user-defined road network via the use of the great
   `OSMNx` –– [Network module](#network-module---querying-road-networks);
2) Load your geospatial data (`CSV`, `Parquet`, or `shapefiles`) using
   its [Loader module](#loader-module---loading-urban-datasets);
3) Wrangle the loaded data with optional [imputation](#preprocessing-module---cleaning-and-filtering-data)
   and [filtering](#preprocessing-module---cleaning-and-filtering-data) to handle _missing coordinates_ or _irrelevant
   regions_ –– [Preprocessing module](#preprocessing-module---cleaning-and-filtering-data);
4) Map data to street nodes, _enrich_ the network (e.g., *averaging building floors per street* or *counting taxi
   pickups per street
   segments*) – no big deal, a factory makes it “easy” to do
   so –– [Enricher module](#enricher-module---mapping-data-to-networks);
5) In order to visualise results _statically_ or
   _interactively_ –– [Visual module](#visual-module---visualising-results);
6) _Optional but save your analysis for later use or sharing with other urban experts._

Though, to answer (II) using the right state-of-the-art open-source initiatives and tools, highly type
safe and tested and documented library is a must. We already are fully highly-typed thanks to BearType, yet we aim at
reaching a decent test coverage and documentation to make the library more robust and user-friendly.

> Who knows— we'd like you to deal with what matters to you; e.g., if you are a machine learning enthusiast, you can
> apply machine learning to the enriched
> networks, if you are a researcher, you can easily map your data to street networks and get insights from them.
> Nonetheless, if you want to contribute to the library, you can easily do so by adding new modules or extending the
> existing ones, and we are happy in advance to welcome you doing so! 🥐

We embrace a **DRY (Do Not Repeat Yourself)** philosophy—focusing on what matters and letting us handle the mapping
intricacies. Of course, I mentioned the `pipeline`, but each of the _steps_ mentioned works independently to each other
🙃!

</details>


See further notebook-based examples in the `examples/` directory. 📓

---

## 🥐 Installation

We *highly* recommend using `uv` for installation from source to avoid the hassle of `Conda` or other package managers.
It is also the fastest known to date on the OSS market and manages dependencies seamlessly without manual environment
activation (Biggest flex!). If you do not want to use `uv`, there are no issues, but we will cover it in the upcoming
documentation – not as follows.

First, ensure `uv` is installed on your machine by
following [these instructions](https://docs.astral.sh/uv/getting-started/installation/).

### Prerequisites

- Install `uv` as described above.
- Clone `Auctus` (required for alpha development) into the same parent directory as `OSMNxMapping`. Use:
  ```bash
  git clone git@github.com:VIDA-NYU/auctus_search.git
  ```
  This step ensures `pyproject.toml` builds `auctus_search` from source during installation, though we plan for
  `auctus_search` to become a PyPi package (`uv add auctus_search` or `pip install auctus_search`) in future releases.

> [!NOTE]  
> Future versions will simplify this process: `auctus_search` will move to PyPi, removing the need for manual cloning,
> and Jupyter extensions will auto-install via `pyproject.toml` configuration.

### Steps

1. Clone the `OSMNxMapping` repository:
   ```bash
   git clone https://github.com/yourusername/OSMNxMapping.git
   cd OSMNxMapping
   ```
2. Lock and sync dependencies with `uv`:
   ```bash
   uv lock
   uv sync
   ```
3. (Recommended) Install Jupyter extensions for interactive visualisations requiring Jupyter widgets:
   ```bash
   uv run jupyter labextension install @jupyter-widgets/jupyterlab-manager
   ```
4. Launch Jupyter Lab to explore `OSMNxMapping` (Way faster than running Jupyter without `uv`):
   ```bash
   uv run --with jupyter jupyter lab
   ```

Voila 🥐 ! You’re all set to explore `OSMNxMapping` in Jupyter Lab.

# Getting Started!

Below are two approaches to get you started with the `OSMNxMapping` library in a Jupyter notebook. These examples are also available in the `examples/` directory as `1-OSMNX_MAPPING_with_Auctus_basics.ipynb` (for the step-by-step approach) and `5-Advanced_Urban_Pipeline_Save_and_Load.ipynb` (for the pipeline approach).

---

<details>
<summary><strong> 🐥Fine-Grained Step-by-Step</strong></summary>

This detailed approach walks you through each step of mapping urban data to a street network using PLUTO (Primary Land Use Tax Lot Output) buildings in New York City as an example. It’s perfect for understanding the full process.

#### Cell 1: Import the Library

```python
import osmnx_mapping as oxm
```

#### Cell 2: Initialise an OSMNxMapping Instance

```python
pluto_buildings = oxm.OSMNxMapping()  # Here, PLUTO buildings represent an urban analysis study of The Primary Land Use Tax Lot Output in New York City, USA. Note that nothing is loaded or queried yet—everything is to be done.
```

#### Cell 3: Search for Datasets

Note: You can always load your dataset manually—see the `/examples` folder for details. Here, we use `Auctus` to search for datasets related to "PLUTO".

```python
collection = pluto_buildings.search_datasets(search_query="PLUTO", display_initial_results=True)

# Search for datasets related to "PLUTO". The `search_datasets` method queries the Auctus API and returns a
# `DatasetCollection`. Setting `display_initial_results=True` shows the initial results interactively in the notebook,
# allowing you to see available datasets right away.

# More parameters like page and size for pagination are available—check the Auctus Search / OSMNxMapping API for details.
```

#### Cell 4: Load the Selected Dataset

```python
dataset = pluto_buildings.load_dataset_from_auctus()

# After selecting a dataset in the previous step, this loads it into memory as a `pandas.DataFrame` (or
# `geopandas.GeoDataFrame` if spatial). By default, it displays an interactive table preview of the dataset.
```

#### Cell 5: Load Your Auctus Dataset into OSMNxMapping

Note: `load_from_dataframe` doesn’t reload the data entirely—it transposes it into a format OSMNxMapping understands.

```python
loaded_data = pluto_buildings.loader.load_from_dataframe(
    input_dataframe=dataset, 
    latitude_column="latitude",  # Assuming the dataset has a column named "latitude" for latitude values
    longitude_column="longitude"  # Assuming the dataset has a column named "longitude" for longitude values
)

pluto_buildings.table_vis.interactive_display(loaded_data)
```

#### Cell 6: Query a Road Network for the Selected Place

```python
graph, nodes, edges = pluto_buildings.network.network_from_place("Manhattan, New York City, USA", render=True)  # render=True shows the plain network.
```

#### Cell 7: Map the Loaded Data to the Nearest Street Nodes

By default, this creates a new column in `loaded_data` with the node ID to which each record (e.g., a building) is closest—key for enrichment.

```python
loaded_data = pluto_buildings.network.map_nearest_street(
    data=loaded_data, 
    longitude_column="longitude", 
    latitude_column="latitude"
)
```

#### Cell 8: Geo Preprocess Your Dataset

First, we impute missing values in the `latitude` and `longitude` columns using `SimpleGeoImputer`, which naively drops rows with missing values. For advanced methods, see the `PreprocessingMixin` API.

```python
loaded_data = (
    pluto_buildings.preprocessing
    .with_default_imputer(latitude_column_name="latitude", longitude_column_name="longitude")
    .transform(input_data=loaded_data)
)
```

Second, we filter data to keep only points within the road network’s bounding box using `BoundingBoxFilter`. See the `PreprocessingMixin` API for other filters.

```python
loaded_data = (
    pluto_buildings.preprocessing
    .with_default_filter(nodes=nodes)
    .transform(input_data=loaded_data)
)
```

#### Cell 9: Enrich the Network with the Loaded Data

We enrich the network by calculating the average number of floors (`numfloors`) per street segment using `CreateEnricher`.

```python
pluto_buildings_enricher = (
    CreateEnricher()
    .with_data(group_by="nearest_node", values_from="numfloors")
    .aggregate_with(method="mean", output_column="avg_numfloors")
)

# Preview the enricher configuration (optional)
print(pluto_buildings_enricher.preview())

# Apply the enricher
enriched_data, graph, nodes, edges = pluto_buildings.enricher.enrich_network(
    input_data=loaded_data,
    input_graph=graph,
    input_nodes=nodes,
    input_edges=edges
)
```

#### Cell 10: Visualise Your Enriched Network

We visualise the enriched network with `StaticVisualiser` (default) for a Matplotlib plot.

```python
viz = pluto_buildings.visual.visualise(graph, edges, "avg_numfloors")
viz
```

Or use `InteractiveVisualiser` for an interactive Folium map.

```python
from osmnx_mapping import InteractiveVisualiser

viz = pluto_buildings.visual(visualiser=InteractiveVisualiser()).visualise(graph, edges, "avg_numfloors")
viz
```

</details>

---

<details>
<summary><strong> 💨 Urban Pipeline: ~10 Lines of Code!</strong></summary>

For a faster, more concise, and reproducible approach, use the `UrbanPipeline` class to chain all steps into a single workflow. Here’s an example with local PLUTO data (`pluto.csv`), as Auctus is not available in a pipeline you may reckon why!

#### Quick Pipeline Example

```python
import osmnx_mapping as oxm
from osmnx_mapping.modules.network import OSMNxNetwork
from osmnx_mapping.modules.loader import CSVLoader
from osmnx_mapping.modules.preprocessing import CreatePreprocessor
from osmnx_mapping.modules.enricher import CreateEnricher
from osmnx_mapping.modules.visualiser import InteractiveVisualiser
from osmnx_mapping.pipeline import UrbanPipeline

# Define the pipeline with all steps
pipeline = UrbanPipeline([
    ("network", OSMNxNetwork(place_name="Manhattan, NYC", network_type="drive")),
    ("load", CSVLoader(file_path="./pluto.csv")),
    ("impute", CreatePreprocessor().with_default_imputer().build()), # yes latitude and longitude based columns are passed during the compose_transform, like X, and Y during a Sklearn pipeline, if modified are passed throughout the steps.
    ("filter", CreatePreprocessor().with_default_filter().build()),  # yes nodes are passed during the compose_transform, like X, and Y during a Sklearn pipeline, if modified are passed throughout the steps.
    ("enrich", CreateEnricher()
        .with_data(group_by="nearest_node", values_from="numfloors")
        .aggregate_with(method="mean", output_column="avg_numfloors")
        .build()),
    ("viz", InteractiveVisualiser())
])

# Execute the pipeline and visualise the result
data, graph, nodes, edges = pipeline.compose_transform("latitude", "longitude")
viz = pipeline.visualise("avg_numfloors", colormap="Greens", tile_provider="CartoDB positron")
viz

# Save the pipeline for reuse
# pipeline.save("pluto_pipeline.joblib")
```

#### What’s Happening? 👀

- **Network**: Queries Manhattan’s road network.
- **Load**: Loads `pluto.csv` locally.
- **Impute/Filter**: Cleans and bounds the data.
- **Enrich**: Averages floors per street segment.
- **Visualise**: Shows an interactive Folium map.
- **Save**: Stores the pipeline for reuse.

This ~10-line pipeline replaces the detailed steps above, offering efficiency and reproducibility. Load it later with `UrbanPipeline.load("pluto_pipeline.joblib")` and visualise again!

> **Note**: Adjust the file path and column names (`latitude`, `longitude`, `numfloors`) to match your local dataset.

</details>

---

Voila! 🥐 Whether you prefer the fine-grained control of the step-by-step approach or the concise reproducible urban pipeline, you’ve successfully mapped urban data to a street network, enriched it, and visualised the results. 🎉

> [!NOTE]  
> More advanced usage is possible—explore the API and `examples/` directory for details!

---

## 🗺️ Roadmap / Future Work

> [!NOTE]  
> For more about future works, explore the `issues` tab above!

1) From labs to more general communities, we want to advance `OSMNxMapping` by attaining large unit-test coverage,
   integrating
   routines via `G.Actions`, and producing thorough documentation for users all around.
2) We are also looking at building a function *f(X, set(Ys))* that could introduce a `MultiAggregatorEnricher` to handle
   multiple
   datasets –– yes, at the same time –– necessitating a rethink of visualisation approaches—brainstorming is underway.
3) Finally, we’re pondering
   whether `X`, currently OSMNx street networks, could evolve to other urban networks, questioning if alternatives exist
   or
   if we might redefine networks beyond roads, with these discussions still in progress.

We'd be welcome to see more `loader`, `geo imputer` and `geo filter` primitives to be pull requested, as well as
`enricher` and `visualiser` primitives to be extended. We are also looking forward to seeing more examples in the
`examples/` directory, and we are happy to welcome you to contribute to the library 🎄

## 🌁 API

> [!IMPORTANT]
> The following project is fully python-typed safe and uses the great [@beartype](https://github.com/beartype/beartype)! It should reduce side effects and better library usability on the user end side.

Users familiar with `data pipelines` will find the modular, `scikit-learn-inspired` design of the `OSMNxMapping` library
clear-cut. For others, believe us it is the way to go!

We offer a set of **mixins** that simplify difficult chores including `data loading`, `road network building`,
`preprocessing`, `enrichment`, and `visualising` of enriched graph data. Your main interface is these mixins, which
neatly wrap the underlying modules for a flawless performance.

<details>
<summary><strong>LoaderMixin</strong> – Load Your Urban Data</summary>

The `LoaderMixin` handles loading geospatial data from files or DataFrames, converting it into a `GeoDataFrame` for
further analysis.

> [!NOTE]  
> Only *.csv*, *.parquet*, and shapefiles are supported for now. If you need additional formats, please let us know!
> Or pssst! You can contribute to the library by adding new loader primitive to the `loader` module.

- **`load_from_file(file_path, latitude_column="", longitude_column="")`**
    - **Purpose**: Loads data from a file (CSV, Parquet, or Shapefile) into a `GeoDataFrame`.
    - **Parameters**:
        - `file_path` (str): Path to the file.
        - `latitude_column` (str, optional): Name of the latitude column.
        - `longitude_column` (str, optional): Name of the longitude column.
    - **Returns**: A `geopandas.GeoDataFrame`.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      # The loader module handles csv, parquet, and shapefiles as a factory that means, no need for you to worry about
      # the file format.
      data = mapping.loader.load_from_file("city_data.csv", latitude_column="lat", longitude_column="lon")
      ```

- **`load_from_dataframe(input_data, latitude_column, longitude_column)`**
    - **Purpose**: Converts a DataFrame to a `GeoDataFrame` using specified lat/lon columns.
    - **Parameters**:
        - `input_data` (pandas.DataFrame or geopandas.GeoDataFrame): The input data.
        - `latitude_column` (str): Latitude column name.
        - `longitude_column` (str): Longitude column name.
    - **Returns**: A `geopandas.GeoDataFrame`.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      import pandas as pd
      df = pd.DataFrame({"lat": [40.7128], "lon": [-74.0060]})
      geo_data = mapping.loader.load_from_dataframe(df, "lat", "lon")
      ```

      Another example is if you are using Auctus loaded selected dataset:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      # Assuming you have loaded a dataset from Auctus into `new_data`
      geo_data = mapping.loader.load_from_dataframe(new_data, "lat", "lon")
      ```

</details>

<details>
<summary><strong>NetworkMixin</strong> – Build and Map Road Networks</summary>

The `NetworkMixin` lets you query road networks from OpenStreetMap and map data points to the nearest street nodes or edges.

- **`network_from_place(place_name, network_type="drive", render=False)`**
    - **Purpose**: Queries a road network for a specified place.
    - **Parameters**:
        - `place_name` (str): Location (e.g., "Manhattan, New York City, USA").
        - `network_type` (str, default="drive"): Type of network ("drive", "walk", "bike").
        - `render` (bool, default=False): If True, displays a plot of the network.
    - **Returns**: A tuple (`networkx.MultiDiGraph`, `geopandas.GeoDataFrame`, `geopandas.GeoDataFrame`) of the graph, nodes, and edges.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      graph, nodes, edges = mapping.network.network_from_place("Manhattan, New York City, USA")
      ```

- **`map_nearest_street(data, longitude_column, latitude_column, output_column="nearest_node", reset_output_column=False, **kwargs)`**
    - **Purpose**: Maps data points to the nearest street nodes in the network.
    - **Parameters**:
        - `data` (geopandas.GeoDataFrame): Input data with lat/lon.
        - `longitude_column` (str): Longitude column name.
        - `latitude_column` (str): Latitude column name.
        - `output_column` (str, default="nearest_node"): Column to store node IDs.
        - `reset_output_column` (bool, default=False): Overwrite existing output column.
        - `**kwargs`: Additional parameters for OSMnx’s `nearest_nodes`.
    - **Returns**: A `geopandas.GeoDataFrame` with mapped nodes.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      # Assuming data is a GeoDataFrame from previous steps (e.g., LoaderMixin)
      mapped_data = mapping.network.map_nearest_street(data, "lon", "lat")
      ```

> [!NOTE]  
> When using the pipeline, it is recommended to configure the network using the `CreateNetwork` factory, which allows specifying mappings for nearest nodes or edges. See the [UrbanPipelineMixin](#urbanpipelinemixin--chain-your-workflow) section for details and examples.

</details>

<details>
<summary><strong>PreprocessingMixin</strong> – Clean and Filter Data</summary>

The `PreprocessingMixin` offers tools to handle missing values and filter data geographically.

> [!IMPORTANT]  
> You **cannot stack** a filter with an imputer (or vice versa) in a single `PreprocessingMixin` instance. Each instance
can only perform **one action**—either imputing or filtering. If you want to stack operations (e.g., impute then filter,
or filter then impute), simply use the pipeline and create two steps—it’s as easy as that! See
the [UrbanPipelineMixin](#urbanpipelinemixin--chain-your-workflow) section for more details on chaining steps.

> [!TIP]  
> Available imputers:
> - `SimpleGeoImputer`: "Naively" drops rows with missing latitude or longitude values.
> - `AddressGeoImputer`: Fills missing lat/lon by geocoding an address column if available (requires
    `address_column_name`).  
    > Available filter:
> - `BoundingBoxFilter`: Keeps only data points within the bounding box of the road network’s nodes (requires `nodes`).

- **`with_imputer(imputer_type, latitude_column_name=None, longitude_column_name=None, **extra_params)`**
    - **Purpose**: Configures an imputer to handle missing lat/lon values.
    - **Parameters**:
        - `imputer_type` (str): Imputer type (e.g., "SimpleGeoImputer", "AddressGeoImputer").
        - `latitude_column_name` (str, optional): Latitude column name. If omitted and used within a pipeline, it will be set by the pipeline’s `compose` method.
        - `longitude_column_name` (str, optional): Longitude column name. If omitted and used within a pipeline, it will be set by the pipeline’s `compose` method.
        - `**extra_params`: Additional parameters (e.g., `address_column_name` for "AddressGeoImputer").
    - **Returns**: The mixin instance for chaining.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      mapping.preprocessing.with_imputer("SimpleGeoImputer", "lat", "lon")
      ```

- **`with_default_imputer(latitude_column_name=None, longitude_column_name=None)`**
    - **Purpose**: Uses a default imputer that drops rows with missing lat/lon.
    - **Parameters**: Same as above, without `imputer_type`.
    - **Returns**: The mixin instance.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      mapping.preprocessing.with_default_imputer("lat", "lon")
      ```

- **`with_filter(filter_type, **extra_params)`**
    - **Purpose**: Configures a filter (e.g., "BoundingBoxFilter").
    - **Parameters**:
        - `filter_type` (str): Filter type.
        - `**extra_params`: Filter-specific parameters (e.g., `nodes` for bounding box).
    - **Returns**: The mixin instance.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      # Assuming nodes is from network_from_place
      graph, nodes, edges = mapping.network.network_from_place("Manhattan, New York City, USA")
      mapping.preprocessing.with_filter("BoundingBoxFilter", nodes=nodes)
      ```

- **`with_default_filter(nodes)`**
    - **Purpose**: Uses a default filter to keep data within the road network’s bounding box.
    - **Parameters**:
        - `nodes` (geopandas.GeoDataFrame): Nodes from the road network defining the bounding box.
    - **Returns**: The mixin instance.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      # Assuming nodes is from network_from_place
      graph, nodes, edges = mapping.network.network_from_place("Manhattan, New York City, USA")
      mapping.preprocessing.with_default_filter(nodes)
      ```

- **`transform(input_data)`**
    - **Purpose**: Applies the configured imputer or filter to the data.
    - **Parameters**:
        - `input_data` (geopandas.GeoDataFrame): Data to preprocess.
    - **Returns**: A preprocessed `geopandas.GeoDataFrame`.
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      data = mapping.loader.load_from_file("city_data.csv", latitude_column="lat", longitude_column="lon")
      mapping.preprocessing.with_default_imputer("lat", "lon")
      cleaned_data = mapping.preprocessing.transform(data)
      ```

</details>

<details>
<summary><strong>EnricherMixin</strong> – Enrich Your Network with Data</summary>

The `EnricherMixin` is the core component of the library, empowering you to aggregate urban data (e.g., traffic counts, building heights) and map it onto a road network's nodes, edges, or both. It's designed for flexibility with advanced customization through the `CreateEnricher` factory, while also offering a simpler default setup for standard use cases.

> [!NOTE]  
> **How the Enricher Works**:  
> The enricher processes data in two key steps:  
> 1. **Aggregation**: It groups your data by a specified column that connects with the graph (e.g., `nearest_node` following `map_nearest_street(.)`) and applies an aggregation method like `mean`, `sum`, or `count` to compute values for each group. For example, it could sum traffic volumes per node.  
> 2. **Mapping**: These aggregated values are then assigned to the network's nodes, edges, or both, based on the `target` parameter. For edges, a method like `average`, `sum`, `max`, or `min` is used to compute values from the connected nodes' values.  
> This process transforms raw data into meaningful insights mapped onto the road network, making it ideal for urban analysis tasks like traffic studies or accident mapping.

---

### Configuring Enrichers with `CreateEnricher` (Recommended Approach)

The `CreateEnricher` factory (an alias for `EnricherFactory`) is the primary and recommended way to configure enrichers. It offers a flexible, step-by-step approach to define how data is aggregated and mapped to the network, giving you full control over the enrichment process.

- **Key Methods**:
    - **`with_data(group_by, values_from=None)`**:
        - **Purpose**: Specifies the column to group data by (e.g., `"nearest_node"`) and, optionally, the column containing values to aggregate (e.g., `"traffic"`).
        - **Example**:
          ```python  
          enricher_factory = CreateEnricher().with_data(group_by="nearest_node", values_from="traffic")  
          ```
    - **`aggregate_with(method, edge_method='average', output_column=None, target='edges')`**:
        - **Purpose**: Configures the aggregation method (e.g., `"sum"`, `"mean"`) and how aggregated values are mapped to the network.
        - **Parameters**:
            - `method` (str): Aggregation method (e.g., `"mean"`, `"sum"`, `"median"`, `"min"`, `"max"`).
            - `edge_method` (str, optional, default="average"): Method to compute edge values (e.g., `"average"`, `"sum"`, `"max"`, `"min"`). Only applicable if `target` includes edges.
            - `output_column` (str, optional): Name of the output column in the target GeoDataFrame(s).
            - `target` (str, optional, default="edges"): Specifies where to apply the enrichment: `"nodes"`, `"edges"`, or `"both"`. If `"nodes"`, values are mapped directly to nodes; if `"edges"`, values are computed for edges using `edge_method`; if `"both"`, enrichment applies to both.
        - **Example**:
          ```python  
          enricher_factory = enricher_factory.aggregate_with(method="sum", edge_method="average", output_column="total_traffic", target="edges")  
          ```
    - **`count_by(edge_method='sum', output_column=None, target='edges')`**:
        - **Purpose**: Configures a counting aggregation (e.g., counting accidents per node), without needing a `values_from` column.
        - **Parameters**:
            - `edge_method` (str, optional, default="sum"): Method to map counts to edges (if `target` includes edges).
            - `output_column` (str, optional): Name of the output column.
            - `target` (str, optional, default="edges"): Specifies where to apply the enrichment: `"nodes"`, `"edges"`, or `"both"`.
        - **Example**:
          ```python  
          enricher_factory = CreateEnricher().with_data(group_by="nearest_node").count_by(edge_method="sum", output_column="accident_count", target="both")  
          ```
    - **`using_enricher(enricher_type)`**:
        - **Purpose**: Selects a specific enricher type (currently, only `"SingleAggregatorEnricher"` is available).
        - **Example**:
          ```python  
          enricher_factory = enricher_factory.using_enricher("SingleAggregatorEnricher")  
          ```
    - **`preview(format="ascii")`**:
        - **Purpose**: Displays a summary of the current configuration, helping you verify settings before building the enricher.
        - **Example**:
          ```python  
          print(enricher_factory.preview())  
          ```
    - **`build()`**:
        - **Purpose**: Constructs and returns the configured `EnricherBase` instance.
        - **Example**:
          ```python  
          enricher = enricher_factory.build()  
          ```

- **Example (Full Configuration)**:
  ```python  
  from osmnx_mapping.modules.enricher import CreateEnricher  
  enricher = (CreateEnricher()  
              .with_data(group_by="nearest_node", values_from="traffic")  
              .aggregate_with(method="sum", edge_method="average", output_column="total_traffic", target="edges")  
              .build())  
  ```

> [!TIP]
> - Use `CreateEnricher` when you need full control over the enrichment process, such as experimenting with different aggregation methods or counting occurrences without a value column.
> - Call `preview()` before `build()` to verify your configuration and catch potential errors early.
> - The `target` parameter determines whether the enrichment is applied to nodes, edges, or both. For `target="both"`, the aggregated values are assigned to both nodes and edges, with edges using the specified `edge_method`.

---

### Using `with_default` for Simplicity (Shortcut for Default Settings)

If you do not need advanced customisation and prefer a quick setup with sensible defaults, the `with_default` method in `EnricherMixin` provides a convenient shortcut. It internally uses `CreateEnricher` with predefined settings, making it ideal for standard use cases.

- **`with_default(group_by_column, values_from_column, output_column="aggregated_value", method="mean", edge_method="average", target="edges")`**
    - **Purpose**: Quickly configures a default enricher using `CreateEnricher` with predefined settings.
    - **Parameters**:
        - `group_by_column` (str): Column to group by (e.g., `"nearest_node"`).
        - `values_from_column` (str): Column to aggregate (e.g., `"traffic"`).
        - `output_column` (str, optional): Name of the output column (default: `"aggregated_value"`).
        - `method` (str, optional): Aggregation method (default: `"mean"`).
        - `edge_method` (str, optional): Edge mapping method (default: `"average"`).
        - `target` (str, optional): Specifies where to apply the enrichment (default: `"edges"`).
    - **Returns**: The `EnricherMixin` instance for method chaining.
    - **Example**:
      ```python  
      import osmnx_mapping as oxm  
      mapping = oxm.OSMNxMapping()  
      mapping.enricher.with_default("nearest_node", "traffic", method="sum", edge_method="average", target="both")  
      ```

> [!TIP]
> - Use `with_default` for standard use cases where you want a quick setup with minimal configuration.
> - If you need more control, switch to `CreateEnricher` for advanced customisation.

---

### Applying the Enricher to the Network

Once configured (using either `CreateEnricher` or `with_default`), the enricher can be applied to the network using the `enrich_network` method.

- **`enrich_network(input_data, input_graph, input_nodes, input_edges, **kwargs)`**
    - **Purpose**: Applies the configured enricher to the road network, enriching the specified target (nodes, edges, or both) with aggregated data.
    - **Parameters**:
        - `input_data` (geopandas.GeoDataFrame): Dataset to enrich with.
        - `input_graph` (networkx.MultiDiGraph): Road network graph.
        - `input_nodes` (geopandas.GeoDataFrame): Network nodes.
        - `input_edges` (geopandas.GeoDataFrame): Network edges.
        - `**kwargs`: Additional options for custom enrichers.
    - **Returns**: A tuple (`GeoDataFrame`, `MultiDiGraph`, `GeoDataFrame`, `GeoDataFrame`) of enriched data, updated graph, updated nodes, and updated edges. Depending on the `target`, the enrichment is applied to nodes, edges, or both.
    - **Example**:
      ```python  
      import osmnx_mapping as oxm  
      mapping = oxm.OSMNxMapping()  
      data = mapping.loader.load_from_file("city_data.csv", latitude_column="lat", longitude_column="lon")  
      graph, nodes, edges = mapping.network.network_from_place("Manhattan, New York City, USA")  
      mapping.enricher.with_default("nearest_node", "traffic", method="sum", edge_method="average", target="edges")  
      enriched_data, graph, nodes, edges = mapping.enricher.enrich_network(data, graph, nodes, edges)  
      ```

> [!TIP]
> - **Counting Occurrences**: Use `count_by` in `CreateEnricher` to count events (e.g., accidents) per group without needing a `values_from` column.
> - **Choosing Between Approaches**: Start with `with_default` for simplicity, but switch to `CreateEnricher` if you need advanced customisation or encounter limitations.
> - **Multiple Enrichers**: When using multiple enrichers in a pipeline, ensure each writes to a unique `output_column` to avoid overwriting data.

</details>

<details>
<summary><strong>VisualMixin</strong> – Visualise Your Results</summary>

The `VisualMixin` provides tools to visualise your enriched network. By default, it uses `StaticVisualiser` for static Matplotlib plots, but you can pass any `VisualiserBase` subclass (e.g., `InteractiveVisualiser` for interactive Folium maps) to the constructor for custom visualisations.

> [!TIP]  
> Available visualisers:
> - `StaticVisualiser`: Generates a static Matplotlib plot of the network (default).
> - `InteractiveVisualiser`: Creates an interactive Folium map for exploration in a browser.

- **`visualise(graph, nodes, edges, result_columns, target="edges", **kwargs)`**
    - **Purpose**: Creates a visualisation of the enriched network using the configured visualiser.
    - **Parameters**:
        - `graph` (networkx.MultiDiGraph): The network graph.
        - `nodes` (geopandas.GeoDataFrame): Network nodes.
        - `edges` (geopandas.GeoDataFrame): Network edges.
        - `result_columns` (str or list of str): Column(s) to visualise. For static visualisers (e.g., `StaticVisualiser`), provide a single string (e.g., `"aggregated_value"`). For interactive visualisers (e.g., `InteractiveVisualiser`), provide a list of strings (e.g., `["column1", "column2"]`) to enable multi-layer visualisation with a dropdown selection.
        - `target` (str, default="edges"): Specifies what to visualise: `"nodes"`, `"edges"`, or `"both"`. Determines whether the visualisation focuses on nodes, edges, or both, based on the enriched data in `result_columns`.
        - `**kwargs`: Visualisation parameters (e.g., `colormap="Blues"` for `StaticVisualiser`, or `tile_provider="CartoDB positron"` for `InteractiveVisualiser`).
    - **Returns**: A Matplotlib figure (for `StaticVisualiser`) or Folium map (for `InteractiveVisualiser`), depending on the visualiser.
    - **Example (Static Visualiser)**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      data = mapping.loader.load_from_file("city_data.csv", latitude_column="lat", longitude_column="lon")
      graph, nodes, edges = mapping.network.network_from_place("Manhattan, New York City, USA")
      mapping.enricher.with_default("nearest_node", "traffic", method="sum", target="edges")
      enriched_data, graph, nodes, edges = mapping.enricher.enrich_network(data, graph, nodes, edges)
      fig = mapping.visual.visualise(graph, nodes, edges, "aggregated_value", target="edges", colormap="Blues")
      ```
    - **Example (Interactive Visualiser)**:
      ```python
      import osmnx_mapping as oxm
      from osmnx_mapping.modules.visualiser.visualisers.interactive_visualiser import InteractiveVisualiser
      mapping = oxm.OSMNxMapping()
      data = mapping.loader.load_from_file("city_data.csv", latitude_column="lat", longitude_column="lon")
      graph, nodes, edges = mapping.network.network_from_place("Manhattan, New York City, USA")
      mapping.enricher.with_default("nearest_node", "traffic", method="sum", target="edges")
      enriched_data, graph, nodes, edges = mapping.enricher.enrich_network(data, graph, nodes, edges)
      # Use InteractiveVisualiser for multi-layer visualisation –– Note that here we assume "aggregated_value" and 
      # "traffic_density" are columns in the enriched edges GeoDataFrame.
      fmap = mapping.visual(InteractiveVisualiser()).visualise(
          graph, nodes, edges, ["aggregated_value", "traffic_density"], target="edges", colormap="Greens", tile_provider="CartoDB positron"
      )
      ```

</details>

<details>
<summary><strong>TableVisMixin</strong> – Interactive Data Exploration</summary>

The `TableVisMixin` offers interactive table visualisations for your data within Jupyter notebooks using the great `Skrub` library.

- **`interactive_display(dataframe, n_rows=10, order_by=None, title="Table Report", column_filters=None, verbose=1)`**
    - **Purpose**: Displays an interactive table for exploring your data.
    - **Parameters**:
        - `dataframe` (pandas.DataFrame or geopandas.GeoDataFrame): The data to display.
        - `n_rows` (int, default=10): Number of rows to show.
        - `order_by` (str or list, optional): Column(s) to sort by.
        - `title` (str, optional): Title of the table.
        - `column_filters` (dict, optional): Filters for specific columns.
        - `verbose` (int, default=1): Verbosity level.
    - **Returns**: Displays the table (no return value).
    - **Example**:
      ```python
      import osmnx_mapping as oxm
      mapping = oxm.OSMNxMapping()
      data = mapping.loader.load_from_file("city_data.csv", latitude_column="lat", longitude_column="lon")
      mapping.table_vis.interactive_display(data, n_rows=5)
      ```

</details>

<details>
<summary><strong>AuctusSearchMixin</strong> – Discover (Urban) Datasets</summary>

The `AuctusSearchMixin` integrates with [Auctus Search](https://github.com/VIDA-NYU/auctus_search), allowing you to discover, profile, and load (urban) datasets directly into your OSMNxMapping workflow.

For detailed usage and examples, please refer to the [Auctus Search README](https://github.com/VIDA-NYU/auctus_search/blob/main/README.md). In the meantime, here are the key methods for using AuctusSearchMixin with OSMNxMapping:

- **`explore_datasets_from_auctus(search_query, page=1, size=10, display_initial_results=False)`**
    - **Purpose**: Searches Auctus for datasets matching the query and optionally displays initial results.
    - **Parameters**:
        - `search_query` (str or list): Search term(s).
        - `page` (int, default=1): Page number (pagination).
        - `size` (int, default=10): Number of results per page.
        - `display_initial_results` (bool, default=False): If True, displays initial search results. Note that if you add `.with_<action>` filtering from AuctusSearch, results display before filtering; use `.display()` afterward to see filtered datasets.
    - **Returns**: An `AuctusDatasetCollection` object. See more in the [Auctus Search README](https://github.com/VIDA-NYU/auctus_search/blob/main/README.md).

- **`profile_dataset_from_auctus()`**
    - **Purpose**: Displays an interactive data profile summary of the selected dataset using the Data Profile Viz library.
    - **Parameters**: None
    - **Returns**: None (displays the profile interactively in the notebook)
    - **Example**:
      ```python
      osmnx_mapping = OSMNxMapping()
      osmnx_mapping.explore_datasets_from_auctus("Taxis")
      # Select a dataset from the interactive results
      osmnx_mapping.profile_dataset_from_auctus()  # Displays the profile using Data Profile Viz.
      ```

- **`load_dataset_from_auctus(display_table=True)`**
    - **Purpose**: Loads the selected dataset from Auctus after choosing one via "Select This Dataset" from the interactive search results. Afterward, you can use the OSMNxMapping Loader module’s `load_from_dataframe` method.
    - **Parameters**:
        - `display_table` (bool, default=True): If True, displays a preview table using `Skrub`.
    - **Returns**: A `pandas.DataFrame` or `geopandas.GeoDataFrame`.

</details>


<details>
<summary><strong>UrbanPipelineMixin</strong> – Chain Your Workflow</summary>

The `UrbanPipelineMixin` enables you to chain multiple steps into a single, reproducible pipeline, modeled after scikit-learn’s `Pipeline`.

> [!IMPORTANT]  
> **Pipeline Restrictions (per configuration):**  
> - **Exactly 1** `NetworkBase` step (e.g., `OSMNxNetwork` or built using `CreateNetwork`).  
> - **Exactly 1** `LoaderBase` step (e.g., `CSVLoader`).  
> - **1 or more** `EnricherBase` steps (e.g., `SingleAggregatorEnricher`).  
> - **0 or 1** `VisualiserBase` step.  
> - **0 or more** `GeoImputerBase` or `GeoFilterBase` steps.  
> Steps must adhere to these constraints, or the pipeline will raise a validation error upon creation or execution.

> [!NOTE]  
> When using multiple `EnricherBase` steps, ensure each writes to a unique `output_column`. If multiple enrichers target 
> the same `output_column`, the last one executed will silently overwrite the others.

---

### **`urban_pipeline(steps)`**
- **Purpose**: Constructs a pipeline from a list of (name, step) tuples, where each step is an instance of a supported base class.  
- **Parameters**:  
  - `steps` (list of tuples): Steps to include, e.g., `[("loader", CSVLoader(...)), ("network", CreateNetwork().with_place(...).build()), ("enricher", CreateEnricher().with_data(...).build())]`.  
- **Returns**: An `UrbanPipeline` object.  
- **Example**:  
  ```python
  import osmnx_mapping as oxm
  from osmnx_mapping.modules.loader.loaders.csv_loader import CSVLoader
  from osmnx_mapping.modules.network import CreateNetwork
  from osmnx_mapping.modules.enricher import CreateEnricher
  mapping = oxm.OSMNxMapping()
  pipeline = mapping.urban_pipeline([
      ("loader", CSVLoader(file_path="city_data.csv")),
      ("network", CreateNetwork().with_place("Manhattan, New York City, USA").with_mapping("node", "lon", "lat", "nearest_node").build()),
      ("enricher1", CreateEnricher()
          .with_data(group_by="nearest_node", values_from="traffic")
          .aggregate_with(method="sum", output_column="total_traffic", target="edges")
          .build()),
      ("enricher2", CreateEnricher()
          .with_data(group_by="nearest_node", values_from="incidents")
          .count_by(output_column="incident_count", target="nodes")
          .build())
  ])
  ```

### **`compose(latitude_column_name, longitude_column_name)`**
- **Purpose**: Configures the pipeline by setting latitude and longitude column names, which are propagated to all relevant steps (e.g., imputers, filters, network mappings) requiring geographic data.  
- **Parameters**:  
  - `latitude_column_name` (str): Name of the latitude column in the input data.  
  - `longitude_column_name` (str): Name of the longitude column in the input data.  
- **Example**:  
  ```python
  pipeline.compose("lat", "lon")
  ```

### **`transform()`**
- **Purpose**: Executes the pipeline after `compose()` has been called, processing the data and returning the results.  
- **Parameters**: None (requires prior `compose()` call).  
- **Returns**: A tuple (`GeoDataFrame`, `MultiDiGraph`, `GeoDataFrame`, `GeoDataFrame`) containing the processed data, network graph, nodes, and edges, respectively.  
- **Example**:  
  ```python
  data, graph, nodes, edges = pipeline.transform()
  ```

### **`compose_transform(latitude_column_name, longitude_column_name)`**
- **Purpose**: Combines configuration and execution into a single step, configuring the pipeline and immediately processing the data.  
- **Parameters**:  
  - `latitude_column_name` (str): Name of the latitude column.  
  - `longitude_column_name` (str): Name of the longitude column.  
- **Returns**: A tuple (`GeoDataFrame`, `MultiDiGraph`, `GeoDataFrame`, `GeoDataFrame`) of processed data, graph, nodes, and edges.  
- **Example**:  
  ```python
  data, graph, nodes, edges = pipeline.compose_transform("lat", "lon")
  ```

### **`visualise(result_columns, **kwargs)`**
- **Purpose**: Visualises the pipeline’s output using the configured `VisualiserBase` step (if present).  
- **Parameters**:  
  - `result_columns` (str or list of str): Column(s) to visualise. Use a single string (e.g., `"total_traffic"`) for static visualisers (e.g., `StaticVisualiser`). Use a list of strings (e.g., `["total_traffic", "incident_count"]`) for interactive visualisers (e.g., `InteractiveVisualiser`) supporting multi-layer singular visualisation.  
  - `**kwargs`: Additional visualisation options (e.g., `colormap="Blues"`, `tile_provider="CartoDB positron"`).  
- **Returns**: A plot (e.g., Matplotlib figure) for static visualisers or an interactive map for interactive visualisers.  
- **Note**: Passing a list to `result_columns` with a static visualiser will raise an error. Ensure the type matches the visualiser used.  
- **Example**:  
  ```python
  # For a static visualiser
  fig = pipeline.visualise("total_traffic", colormap="Blues")
  # For an interactive visualiser
  fmap = pipeline.visualise(["total_traffic", "incident_count"], colormap="Greens", tile_provider="CartoDB positron")
  ```

### **`save(filepath)` / `load(filepath)`**
- **Purpose**: Saves the pipeline to a file or loads a previously saved pipeline for reuse.  
- **Parameters**:  
  - `filepath` (str): Path to the file (e.g., `"my_pipeline.joblib"`).  
- **Example**:  
  ```python
  pipeline.save("my_pipeline.joblib")
  loaded_pipeline = UrbanPipeline.load("my_pipeline.joblib")
  ```

### **Additional Features** (scikit-learn style)
- **`named_steps`**: Access pipeline steps by name, e.g., `pipeline.named_steps["loader"]`.  
- **`get_step_names()`**: Returns a list of all step names in the pipeline.  
- **`get_step(name)`**: Retrieves a specific step by its name.  
- **`get_params(deep=True)`**: Intended to return all pipeline parameters (not yet implemented).  
- **`set_params(**kwargs)`**: Intended to update pipeline parameters (not yet implemented).  

> [!NOTE]  
> The `get_params` and `set_params` methods are planned features and are not functional in the current release.

</details>

> [!IMPORTANT]  
> Full documentation is forthcoming; Hence, expect some breaking changes in the API – Bare wth us a doc is cooking-up! ⚠️

---

## 📓 Examples

Check out the `examples/` directory in the [OSMNxMapping repo](https://github.com/VIDA-NYU/OSMNXMapping) for more
detailed Jupyter notebook examples.

---

## Licence

`OSMNxMapping` is released under the [MIT Licence](./LICENCE).
