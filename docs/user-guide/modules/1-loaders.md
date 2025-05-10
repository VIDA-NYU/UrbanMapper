# 🌇 Loaders: Bringing Your Data to Life

Loaders are your gateway into `UrbanMapper`—they take your raw data, whether it’s stashed in a `CSV`, a `Shapefile`, or
already `loaded in memory as a DataFrame`, and turn it into a `GeoDataFrame` that `UrbanMapper` can work with seamlessly.
Think of loaders as the bridge between your data and the spatial insights you’re after, making sure everything is ready
for `mapping`, `enrichment`, and `analysis`.

!!! question "Why Loaders Matter?"
    Loaders aren’t just about importing data—they standardise it into a format (`GeoDataFrame`) that powers `UrbanMapper`’s workflows. Without them, your data would be like a puzzle with missing pieces, unable to connect to the urban layers you want to explore.

## 📂 Types of Loaders

`UrbanMapper` provides loaders for a variety of data formats, so you can bring in your data however it’s stored:

- **CSV Loader**: Great for tabular data like spreadsheets. Tell it where your coordinates are, and it’ll handle the
rest.
- **Shapefile Loader**: A go-to for GIS pros—loads ESRI Shapefiles with all their spatial details intact. We automatically infer the coordinates based on the geometry of each records in the dataset.
- **Parquet Loader**: Perfect for large datasets—reads efficient Parquet files while preserving geospatial info.
- **Hugging Face Loader**: Seamlessly load datasets hosted on the Hugging Face Hub. Ideal for accessing curated datasets for urban analysis.

And if your data’s already loaded by any means in your Python script or Notebook's cell:

- **From (Geo)Pandas DataFrame**: Have a DataFrame ready? Load it up with `with_dataframe` instead of `from_file` and you're good to go.

!!! question "Which Loader Should I Use?"
    It does not really matter which loader you choose, as `UrbanMapper` will automatically infer the correct one based on the file extension or source type. However, here are some guidelines:
        
    - **CSV**: For simple, tabular data (e.g., taxi trip logs).
    - **Shapefile**: For GIS-ready files with built-in geometry.
    - **Parquet**: For large, optimised datasets.
    - **Hugging Face**: For accessing curated datasets directly from the Hugging Face Hub.
    - **DataFrames**: When your data’s already in memory from another process.

## 🏗️ Instantiating your first `Loader`

Setting up a loader is as easy as pie—`UrbanMapper`’s factory pattern lets you customise it step-by-step. Here’s how to get started.

### Basic Example: Loading from a CSV
Imagine you’ve got taxi trip data in a CSV file:

```python
import urban_mapper as um

loader = (
    um.loader
    .from_file("./data/taxi_trips.csv")
    .with_columns(longitude_column="pickup_longitude", latitude_column="pickup_latitude")
    .build()
)
```

- **What’s going on?**
  - `from_file("./data/taxi_trips.csv")`: Points to your CSV file.
  - `with_columns(...)`: Tells `UrbanMapper` which columns hold your coordinates.
  - `build()`: Locks it in, creating your loader.

### More Ways to Load Data
UrbanMapper’s got options for a lot of scenarios:

- **From a Shapefile**: For spatial data straight from GIS tools.
  ```python
  loader = (
      um.loader
      .from_file("./data/neighborhoods.shp")
      .build()
  )
  ```
- **From a Parquet File**: Fast and efficient for big data.
  ```python
  loader = (
      um.loader
      .from_file("./data/taxi_trips.parquet")
      .with_columns(longitude_column="pickup_longitude", latitude_column="pickup_latitude")
      .build()
  )
  ```
- **From a Hugging Face Dataset**: Load curated datasets directly from the Hugging Face Hub.
  ```python
  loader = (
      um.loader
      .from_huggingface("oscur/pluto")  # Replace with your desired dataset
      .with_columns(longitude_column="longitude", latitude_column="latitude")
      .build()
  )
  ```
- **From a Pandas DataFrame**: When your data’s already in memory.
  ```python
  import pandas as pd
  df = pd.read_csv("./data/taxi_trips.csv")
  loader = (
      um.loader
      .from_dataframe(df)
      .with_columns(longitude_column="pickup_longitude", latitude_column="pickup_latitude")
      .build()
  )
  ```
- **From a GeoPandas GeoDataFrame**: For prepped geospatial data.
  ```python
  import geopandas as gpd
  gdf = gpd.read_file("./data/neighborhoods.shp")
  loader = (
      um.loader
      .from_dataframe(gdf)
      .build()
  )
  ```

## 🌍 Setting the Coordinate Reference System (CRS)

`UrbanMapper` defaults to `WGS84 (EPSG:4326)`—the universal language of latitude and longitude. But if your data uses a different CRS, you can set it:

```python
loader = (
    um.loader
    .from_file("./data/taxi_trips.csv")
    .with_columns(longitude_column="pickup_longitude", latitude_column="pickup_latitude")
    .with_crs("EPSG:3857")  # Web Mercator, for example
    .build()
)
```

- **Why bother?** A mismatched CRS is like using a map from the wrong city—setting it right keeps your data aligned with the urban layers and the continuing `UrbanMapper`'s workflow.

## 📦 Loading the Data

Once your loader’s built, fetching the data is a snap:

```python
gdf = loader.load()
print(f"Number of rows: {len(gdf)}")
print(f"Columns: {gdf.columns.tolist()}")
print(f"CRS: {gdf.crs}")
```

- **Pro tip**: Try `gdf.head()` to sneak a peek or `gdf.explore()` for an interactive map right in your notebook.

## 🔄 Loaders in a Pipeline

`Loaders` shine as the first step in an `UrbanMapper` pipeline, feeding data into the next stages:

```python
from urban_mapper.pipeline import UrbanPipeline

pipeline = UrbanPipeline([
    ("loader", loader),
    ("urban_layer", urban_layer),
    # Add more components like imputers or enrichers
])

mapped_data, enriched_layer = pipeline.transform()
```

- **Why pipelines?** They’re like a conveyor belt—`loaders` start the process, passing your data smoothly to mapping and enrichment.

–––

[Wants to know more? See this Feature Request :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/issues/8){ .md-button }
