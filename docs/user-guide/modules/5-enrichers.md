# 🌇 Enrichers: Turning Data into Urban Insights

`Enrichers` are the heart of `UrbanMapper`’s analysis—they take your `mapped data` and `transform it` into meaningful
`statistics`, like `counting taxi pickups` at each `intersection` or `averaging building heights` per `neighborhood`. These
insights breathe life into your considered plain `urban layers`, turning raw numbers into stories about the city. Whether you’re counting,
summing, or applying custom calculations, enrichers make your data speak.

!!! question "Why Enrichers Matter ?"
    `Enrichers` are where your data starts to make sense. They aggregate and summarise, turning scattered points into patterns—like revealing the busiest street corners or the priciest neighborhoods. Without them, your `urban layer` is just a plain map; with them, it’s a window into the city’s pulse.

## 🛠️ Types of Enrichers

`UrbanMapper` currently offers one powerful enricher type that handles a range of operations:

### `SingleAggregatorEnricher`

This enricher can:

- **Count** the number of points (e.g., taxi pickups) mapped to each urban feature.
- **Aggregate** values (e.g., fare amounts) using methods like `mean`, `sum`, or even custom functions.

## 📊 Aggregation Methods

`UrbanMapper` supports several built-in aggregation methods:

- **mean**: Average value (e.g., average fare per intersection).
- **sum**: Total value (e.g., total revenue per street).
- **median**: Middle value (e.g., median building height).
- **min**: Smallest value (e.g., lowest rent).
- **max**: Largest value (e.g., tallest building).

And if that’s not enough, you can plug in your own custom functions—like weighted averages or specialised metrics.

!!! question "Which Aggregation Should I Use?"
    - **Count** for frequency (e.g., how many events happen here?).
    - **Mean** for averages (e.g., what’s typical here?).
    - **Sum** for totals (e.g., what’s the overall impact here?).
    - **Custom** for unique insights (e.g., weighted scores or complex calculations).

## 🏗️ Instantiate your first Enrichers

`UrbanMapper`’s factory pattern makes building enrichers intuitive. Let’s see how.

### Counting Points
Want to know `how many taxi pickups` happen at each `intersection`?

```python
import urban_mapper as um

count_enricher = (
    um.UrbanMapper()
    .enricher
    .with_data(group_by="nearest_intersection")
    .count_by(output_column="pickup_count")
    .build()
)
```

**What’s happening?**:

  - `with_data(group_by="nearest_intersection")`: Groups data by the mapped intersection. Done during the `Urban Layer`'s step.
  - `count_by(output_column="pickup_count")`: Counts the points in each group and stores the result in `pickup_count`.

### Aggregating Values
How about finding the `average fare amount` per `intersection`?

```python
avg_enricher = (
    um.UrbanMapper()
    .enricher
    .with_data(group_by="nearest_intersection", values_from="fare_amount")
    .aggregate_by(method="mean", output_column="avg_fare")
    .build()
)
```

- **Extra step**: `values_from="fare_amount"` tells the enricher which column to aggregate.

### Custom Aggregation
Got a unique metric in mind? Define your own function:

```python
def weighted_average(series):
    weights = [1 if val < 10 else 2 for val in series]
    return sum(series * weights) / sum(weights)

custom_enricher = (
    um.UrbanMapper()
    .enricher
    .with_data(group_by="nearest_intersection", values_from="fare_amount")
    .aggregate_by(method=weighted_average, output_column="weighted_avg_fare")
    .build()
)
```

- **Why custom?** Tailor your analysis to specific needs—like giving more weight to higher fares. Or when dealing with categorical-based attributes, it helps to use functions like `mode`.

## 📈 Enriching Your Data

Once your `enricher` is ready, applying it is straightforward:

```python
enriched_layer = count_enricher.enrich(mapped_data, urban_layer)
```

- **Pro tip**: Peek at your enriched layer with `enriched_layer.get_layer().head()` to see the new columns in action.

### Checking the Results
Want to know what you’ve uncovered? Summarise your enriched data:

```python
print(f"Enriched features: {len(enriched_layer.get_layer())}")
print(f"Enriched columns: {enriched_layer.get_layer().columns.tolist()}")
print(f"Pickup count stats:\n{enriched_layer.get_layer()['pickup_count'].describe()}")
```

## 🔄 Enrichers in Pipelines

`Enrichers` fit perfectly into `UrbanMapper` pipelines, typically after `filtering`:

```python
from urban_mapper.pipeline import UrbanPipeline

pipeline = UrbanPipeline([
    ("loader", loader),
    ("urban_layer", urban_layer),
    ("imputer", imputer),
    ("filter", filter_step),
    ("enricher", count_enricher),
    # Next could be the visualiser
])

mapped_data, enriched_layer = pipeline.transform()
```

### Multiple Enrichers
Need more insights? Stack `enrichers` to calculate different metrics:

```python
pipeline = UrbanPipeline([
    ("loader", loader),
    ("urban_layer", urban_layer),
    ("imputer", imputer),
    ("filter", filter_step),
    ("count_enricher", count_enricher),
    ("avg_fare_enricher", avg_enricher),
    ("max_fare_enricher", max_enricher),
    # Next could be the visualiser
])
```

- **Why multiple?** Each enricher adds a new layer of insight—like counting pickups, averaging fares, and finding the highest fare, all in one go. You can think of very complex urban analysis, they require more than one enricher.

–––

[Wants to know more? See this Feature Request :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/issues/11){ .md-button }
