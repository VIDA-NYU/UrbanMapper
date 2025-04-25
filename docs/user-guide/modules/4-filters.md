# 🌇 Filters: Zooming In on / Keeping What Matters

Filters in `UrbanMapper` are your tools for sharpening the focus of your urban data analysis. They restrict data based on
spatial or attribute criteria, letting you zero in on the subsets that matter most. Whether you’re analysing a single
neighborhood or a sprawling boroughs area, filters help you cut through the noise and get to the insights faster.

!!! question "Why Use Filters?"
    You do an analysis on `Downtown Brooklyn, New York City, USA`. Most of the time you will have data of the whole `NYC` city. You do not want the data points from `Queens` or `Staten Island` to be included in your analysis. Filters help you to restrict the data to the area of interest, so you can focus on what matters most.

## 🗺️ Types of Filters

Right now, `UrbanMapper` offers one key filter type:

### BoundingBoxFilter

The **BoundingBoxFilter** is your spatial gatekeeper. It restricts data to the bounding box of your `urban layer`,
ensuring all data points fall within the region you’re studying—like fencing off a city block to focus solely on what’s
inside.

!!! question "What’s a Bounding Box?"
    Think of it as the smallest rectangle that fully encloses your urban layer’s spatial extent. It’s the frame that defines your analysis area.

## 🏗️ Instantiating your first Filters

Building a `filter` in `UrbanMapper` is a breeze thanks to its factory pattern. Here’s how to create a `BoundingBoxFilter`:

```python
import urban_mapper as um

# Create a BoundingBoxFilter
filter_step = (
    um.UrbanMapper()
    .filter
    .with_type("BoundingBoxFilter")
    .build()
)
```

### Filtering Data

Once your `filter` is ready, apply it to your `GeoDataFrame` to trim the data:

```python
# Apply the filter to a GeoDataFrame
filtered_gdf = filter_step.transform(gdf, urban_layer)

# Check the results
print(f"Original rows: {len(gdf)}")
print(f"Filtered rows: {len(filtered_gdf)}")
print(f"Removed rows: {len(gdf) - len(filtered_gdf)}")
```

- **Pro tip**: Visualise your filtered data with `filtered_gdf.explore()` to confirm it matches your urban layer’s bounds.

## 🔄 Filters in Pipelines

`Filters` shine in `UrbanMapper` pipelines, typically slotted between the imputer and enricher steps. 
They keep your pipeline lean by passing only the most relevant data downstream. Here’s an example:

```python
from urban_mapper.pipeline import UrbanPipeline

# Build a pipeline with a filter
pipeline = UrbanPipeline([
    ("loader", loader),
    ("urban_layer", urban_layer),
    ("imputer", imputer),
    ("filter", filter_step),
    # Enricher and Visualiser could be next.
])

# Run it
mapped_data, enriched_layer = pipeline.transform()
```

**Multiple Filters**

Though only the `BoundingBoxFilter` is available now, `UrbanMapper`’s design supports multiple filters applied in sequence. 
Here’s a sneak peek at how that might look:

```python
# Hypothetical pipeline with multiple filters
pipeline = UrbanPipeline([
    ("urban_layer", urban_layer),
    ("loader", loader),
    ("bbox_filter", bbox_filter),
    ("time_filter", time_filter),  # Coming soon? Contribute!
    ("enricher", enricher),
    ("visualiser", visualiser)
])
```

## 🚀 Future Filter Types

The `BoundingBoxFilter` is just the beginning. `UrbanMapper`’s flexible architecture is ready for more filter types down the road, such as:

- **TimeFilter**: Narrow data to specific time ranges.
- **AttributeFilter**: Target data with certain attribute values.
- **DistanceFilter**: Focus on data near key features.
- **TypeFilter**: Hone in on specific urban feature types.

These additions will give you even finer control over your analyses—stay tuned! Or contribute yourself!

–––

[Wants to know more? See this Feature Request :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/issues/5){ .md-button }
