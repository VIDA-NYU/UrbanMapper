# 🌇 Imputers: Filling the Gaps in Your Data

`Imputers` are essential tools in `UrbanMapper` for handling missing or invalid geographic data. They ensure your dataset is
clean and complete, so you can confidently map it to` urban layers` and extract meaningful insights. Think of `imputers` as
the janitors of your data—quietly tidying up so you can focus on the big picture. Without them, `gaps` in your coordinates
could derail your analysis, but with `imputers`, your data stays solid and ready for action.

## 🛠️ Types of Imputers

`UrbanMapper` provides two handy imputers to tackle missing data:

- **SimpleGeoImputer**: The straightforward cleaner. It drops rows with missing or invalid coordinates. Use this when you’ve got just a few gaps that won’t impact your results.
- **AddressGeoImputer**: The smart rescuer. It fills in missing coordinates by geocoding address data, saving rows that would otherwise be lost. Perfect when your dataset has reliable addresses but spotty coordinates.

!!! question "Which Imputer Should I Use?"
    - **SimpleGeoImputer**: Best for minimal missing data you can afford to lose.
    - **AddressGeoImputer**: Ideal when address info can plug the holes in your coordinates.

## 🏗️ Instantiate your first Imputers

`UrbanMapper`’s factory pattern makes setting up `imputers` a breeze. Let’s walk through it.

### Basic Example: `SimpleGeoImputer`
Got a dataset of taxi trips with some missing pickup coordinates? Here’s how to clean it:

```python
import urban_mapper as um

simple_imputer = (
    um.UrbamMapper()
    .imputer
    .with_type("SimpleGeoImputer")
    .on_columns("pickup_longitude", "pickup_latitude")
    .build()
)
```

**What’s happening?**:

  - `with_type("SimpleGeoImputer")`: Selects the simple imputer.
  - `on_columns(...)`: Targets your coordinate columns.
  - `build()`: Creates the imputer, ready to roll.

### Address-Based Imputation
If you’ve got address data to lean on, use `AddressGeoImputer`:

```python
address_imputer = (
    um.UrbamMapper()
    .imputer
    .with_type("AddressGeoImputer")
    .on_columns(
        "pickup_longitude",
        "pickup_latitude",
        "<your_address_column>" # passing the address column's name as kwargs.
    )
    .build()
)
```

## 🧹 Using Imputers

Once your imputer is `built`, applying it is simple.

### Imputing Data
Clean your DataFrame like this:

```python
imputed_df = simple_imputer.impute(df)
```

For `AddressGeoImputer`, it’ll geocode addresses to fill in missing coordinates—same process, smarter fix.
Note that depending on the number, it could take a while to geocode all the addresses.

### Checking the Impact
See how much data you’re losing or saving:

```python
original_rows = len(df)
imputed_df = simple_imputer.impute(df)
dropped = original_rows - len(imputed_df)
print(f"Dropped {dropped} rows ({dropped / original_rows * 100:.2f}%)")
```

!!! tip "Keep an Eye on Data Loss"
    After `imputing`, check the drop rate. Losing too much? Switch to `AddressGeoImputer` or tweak your dataset.

## 🔄 Imputers in Pipelines

Imputers fit neatly into `UrbanMapper` pipelines, cleaning data right after loading:

```python
from urban_mapper.pipeline import UrbanPipeline

pipeline = UrbanPipeline([
    ("loader", loader),
    ("urban_layer", urban_layer),
    ("imputer", simple_imputer),
    # Add filters or enrichers as needed
])

mapped_data, enriched_layer = pipeline.transform()
```

**Multiple Imputers**

For datasets with multiple coordinate sets (e.g., pickup and dropoff), stack `imputers`:

```python
pickup_imputer = (
    um.UrbamMapper()
    .imputer
    .with_type("SimpleGeoImputer")
    .on_columns("pickup_longitude", "pickup_latitude")
    .build()
)

dropoff_imputer = (
    um.UrbamMapper()
    .imputer
    .with_type("SimpleGeoImputer")
    .on_columns("dropoff_longitude", "dropoff_latitude")
    .build()
)

pipeline = UrbanPipeline([
    ("loader", loader),
    ("urban_layer", urban_layer),
    ("pickup_imputer", pickup_imputer),
    ("dropoff_imputer", dropoff_imputer),
])
```

!!! note "A Safety Net"
    Even with clean data, an imputer in your pipeline catches sneaky missing values, keeping your analysis robust.

–––

[Wants to know more? See this Feature Request :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/issues/4){ .md-button }
