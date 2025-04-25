# 🌇 Urban Layers: Your Analysis' Foundation

`Urban Layers` are the foundation of `UrbanMapper`—the spatial canvases on which your data is displayed. These layers
provide structure for urban insights, such as mapping taxi trips to busy `intersections` or analysing `neighbourhood`
demographics. Consider them the `streets`, `districts`, and landmarks of your analysis, ready for data enrichment.
As a result, the `plain` urban layers will be enriched & augmented later on with urban datasets computed information.

!!! question "Why Urban Layers Matter ?"
    `Urban Layers` aren’t just maps—they’re your entry point to spatial analysis. 
     By choosing the right urban layer, you’re setting the stage for everything that follows, 
     from data mapping to enrichment and visualisation. A urban layer needs to be wisely picked depending
     on your urban dataset you want to play with.

# 🗺️ Types of Urban Layers

`UrbanMapper` offers a variety of layers to suit your needs, grouped into three main categories, presented below as tabs for easy exploration.

=== "🛣️ Street Network Layers"
    These layers focus on the physical infrastructure of a city:

    1. [x] **Streets Roads** –– `UrbanMapper` can load street road networks from `OpenStreetMap` (OSM) using `OSMNx`.
    2. [x] **Streets Intersections** –– `UrbanMapper` can load street intersections from `OpenStreetMap` (OSM) using `OSMNx`.
    3. [x] **Sidewalks** –– `UrbanMapper` can load sidewalk via `Tile2Net` using Deep Learning for automated mapping of pedestrian infrastructure from aerial imagery.
    4. [x] **Cross Walks** –– `UrbanMapper` can load crosswalk via `Tile2Net` using Deep Learning for automated mapping of pedestrian infrastructure from aerial imagery.
    5. [x] **Cities' Features** -- `Urban Mapper` can load OSM cities features such as buildings, parks, Bike Lanes etc. via `OSMNx` API.

=== "🏙️ Region Layers"
    These layers define administrative or geographic boundaries:

    6. [x] **Region Neighborhoods** –– `UrbanMapper` can load neighborhoods boundaries from `OpenStreetMap` (OSM) using `OSMNx` Features module.
    7. [x] **Region Cities** –– `UrbanMapper` can load cities boundaries from `OpenStreetMap` (OSM) using `OSMNx` Features module.
    8. [x] **Region States** –– `UrbanMapper` can load states boundaries from `OpenStreetMap` (OSM) using `OSMNx` Features module.
    9. [x] **Region Countries** –– `UrbanMapper` can load countries boundaries from `OpenStreetMap` (OSM) using `OSMNx` Features module.

=== "🛠️ Custom Layers"
    10. [x] **Custom Urban Layer** (`custom_urban_layer`): can load your own spatial data layer in a geojson or shapefile format using `GeoPandas`. This is useful for integrating proprietary datasets or specialised urban features that the above does not provide easily.

!!! question "Which Layer Should I Choose?"
    Everything is relative but some hints could be:

    - **For traffic or mobility studies**: Start with `streets_roads` or `streets_intersections`.
    - **For demographic or policy analysis**: `region_neighborhoods` or `region_cities` are your go-tos.
    - **For something unique / private**: Use `custom_urban_layer` to integrate your own data.

## 🏗️ Instantiating your first Urban Layers

Creating a layer is like sketching the outline of your analysis—it’s quick, flexible, and tailored to your needs. 
Here’s how to get started.

### Basic Example
Let’s say you want to analyse `street intersections` in `Manhattan`:

```python
import urban_mapper as um

urban_layer = (
    um.urban_layer
    .with_type("streets_intersections")
    .from_place("Manhattan, New York City, USA", network_type="drive")
    .build()
)
```

**What’s happening here?**:

  - `with_type("streets_intersections")`: You’re choosing intersections as your layer.
  - `from_place("Manhattan, New York City, USA", network_type="drive")`: You’re pulling data from OpenStreetMap for drivable roads in Manhattan.
  - `build()`: This seals the deal, creating your layer.

### More Ways to Create Layers
`UrbanMapper` gives you flexibility in sourcing your layers:

- **From a Bounding Box**: Define your area with coordinates.
  ```python
  urban_layer = (
      um.urban_layer
      .with_type("streets_roads")
      .from_bbox([-74.01, 40.70, -73.96, 40.75], network_type="drive")
      .build()
  )
  ```
- **From a Point and Distance radius around**: Center your layer on a specific location.
  ```python
  urban_layer = (
      um.urban_layer
      .with_type("streets_intersections")
      .from_point((-73.98, 40.73), distance=1000, network_type="drive")
      .build()
  )
  ```
- **From an Address**: Use a street address as your starting point.
  ```python
  urban_layer = (
      um.urban_layer
      .with_type("region_neighborhoods")
      .from_address("370 Jay St, Brooklyn, NY 11201, USA", distance=500)
      .build()
  )
  ```
- **From a File**: Load your own spatial data for custom layers.
  ```python
  urban_layer = (
      um.urban_layer
      .with_type("custom_urban_layer")
      .from_file("./path/to/custom_areas.geojson") # Shapefile is also supported
      .build()
  )
  ```

## 🧭 Mapping Data to Urban Layers

Mapping is where your data meets the city—linking points (like taxi pickups) to the nearest urban feature (like an intersection). This step is crucial for enriching your layers with real-world insights.

### How to Map
Here’s how to set up mapping for your layer:

```python
urban_layer = (
    um.urban_layer
    .with_type("streets_intersections")
    .with_mapping( 
        longitude_column="pickup_longitude",
        latitude_column="pickup_latitude",
        output_column="nearest_intersection",
        threshold_distance=50  # meters
    )
    .from_place("Manhattan, New York City, USA")
    .build()
)
```

**What’s this doing?**:

  - `with_mapping(...)`: You’re telling `UrbanMapper` how to connect your data points to the layer. you are setting how should the data you will load / have loaded should be mapped to the layer. The how it is getting mapped, is depending on the urban layer's type you choose. If you choose streets roads, it'll be mapping to the nearest street, while if you choose streets intersections, it'll be mapping to the nearest intersection.
  - `longitude_column` and `latitude_column`: The coordinates in your dataset.
  - `output_column`: Where the nearest feature (e.g., intersection) will be stored.
  - `threshold_distance`: Only map points within 50 meters—beyond that, they’re ignored. It's optional.

!!! question "Why Mapping Matters"
    Mapping is the **bridge** between your raw data and spatial insights. Once mapped, you can enrich / augment your layer with aggregations—like counting taxi pickups per intersection or averaging building heights per neighborhood.

### Multiple Mappings
Need to map multiple sets of points? No problem:

```python
urban_layer = (
    um.urban_layer
    .with_type("streets_intersections")
    .with_mapping(
        longitude_column="pickup_longitude",
        latitude_column="pickup_latitude",
        output_column="pickup_intersection"
    )
    .with_mapping(
        longitude_column="dropoff_longitude",
        latitude_column="dropoff_latitude",
        output_column="dropoff_intersection"
    )
    .from_place("Manhattan, New York City, USA")
    .build()
)
```

- **Use case**: Analysing both pickup and dropoff patterns in a taxi trip dataset.

## 🚦 Network Types (For `OSMnx` Layers)

When working with street networks, you can specify the type of network:

- `"drive"`: Focus on roads for vehicles.
- `"walk"`: Pedestrian paths and sidewalks.
- `"bike"`: Bike lanes and paths.
- `"all"`: Everything—roads, paths, and more.

```python
urban_layer = (
    um.urban_layer
    .with_type("streets_roads")
    .from_place("Central Park, New York City", network_type="walk")
    .build()
)
```

- **Why choose "walk"?**: Perfect for analysing pedestrian activity or park accessibility.

Further details on network types can be found in the [OSMnx documentation](https://osmnx.readthedocs.io/en/stable/).
We wrap the `OSMNx` API for some of the urban layers.

## 🛠️ Custom Urban Layers

Got your own spatial data? Bring it in with a custom layer:

```python
custom_layer = (
    um.urban_layer
    .with_type("custom_urban_layer")
    .from_file("./path/to/your_data.geojson")
    .build()
)
```

- **Ideas for custom layers**: 
  - Proprietary zoning data
  - Custom-defined districts
  - Specialised infrastructure like bike-sharing stations
  - Any of the above layers does not match your need / request.

## 📊 Accessing Urban Layer Data

`Urban Layers` are powered by `GeoPandas` `GeoDataFrames`—easy to inspect and manipulate:

```python
gdf = urban_layer.gdf
print(f"Layer type: {urban_layer.type}")
print(f"Number of features: {len(gdf)}")
print(f"CRS: {gdf.crs}")
```

- **Pro tip**: Use `gdf.explore()` for a quick interactive map of your layer.

–––

[Wants to know more? See this Feature Request :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/issues/18){ .md-button }
