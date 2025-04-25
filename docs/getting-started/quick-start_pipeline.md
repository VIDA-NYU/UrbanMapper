# 🌇 `Getting Started with Pipeline` guide!

!!! warning "This is the second entry point out of how to get started with `UrbanMapper`"
    Make sure to have walked through the first entry point out of how to get started with `UrbanMapper` before diving into
    this one. Namely, the Getting Started With Step-By-Step page.

In this guide, we introduce you to `UrbanMapper`’s pipeline approach—a rather concise way to streamline your urban data
analysis. If you’re familiar with `scikit-learn’s` [pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html), 
you’ll find the philosophy here strikingly similar. Much like how scikit-learn allows you to chain `data preprocessing` 
and modeling `steps` into a single workflow, `UrbanMapper`’s pipeline lets you stack urban analysis `steps`—such as 
`loading` data, `processing` it, `enriching` it, and `visualising` it—and execute them all at once. 

This approach ensures your workflow is concise, reproducible, and easily shareable with others 🎉

!!! info "The Story Behind the Pipeline Approach"
    **Picture** yourself as an `urban planner `tasked with analysing building data across a _sprawling_ city. 
    Without a `pipeline`, you’d be juggling multiple tasks manually: `loading` the raw data, `cleaning` up missing entries,
    `filtering` out irrelevant parts, `enriching` it with additional context, and finally creating a `visualisation`. 
    Each step demands _precision_, and if you need to redo the analysis or pass it to a _teammate_, you might forget a step
    or introduce errors. If you would like to re-execute your code in _ten_ years, you'd have to read through a 
    bunch of code to understand what you did, maybe you forgot to remove some `tweaks` you did to your code workflow,
    introducing _side effects_ and _unnecessary_ complexity. Anyway, what you are looking for is a clean and simple way to
    stack all these steps together, so you can focus on the analysis rather than the _nitty-gritty_ of data wrangling.

    Now, enter **UrbanMapper’s pipeline**. You define each step upfront—`load`, `process`, `enrich`, `visualise`—and chain them 
    together into one seamless sequence. With a single command, the entire workflow runs from `start` to `finish`.
    _The result?_ A `consistent`, `reproducible` analysis that you can rerun anytime or even better, `share` with others to 
    replicate your work exactly. It’s like handing over a set of foolproof instructions: anyone can follow them and 
    build the same result. Great for research papers' reproducibility, _right?_

To get started, we'll pick the same `PLUTO` dataset, a comprehensive land use and geographic dataset at the tax lot
level, which contains over seventy fields derived from data maintained by city agencies. This dataset is adequate enough for
urban analysis, and we will use it to explore the `Downtown Brooklyn` area in New York City. More specifically, we will
be using the `PLUTO` dataset to create an interactive map that visualises the average number of building floors per
intersection in the `Downtown Brooklyn, New York City, USA` area.

All that in a single pipeline manner! 🚀

_Dataset's source:_
> PLUTO: Extensive land use and geographic data at the tax lot level. The PLUTO files contain more than seventy fields
> derived from data maintained by city agencies.

- PLUTO data from [NYC Open Data](https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change).

!!! tip "Download all data without complicating yourself?"
    You also can download the public datasets used throughout all examples including this current's one via two channels.
    
    - **Channel 1: Our Google Drive public folder**
        - **Option A:** Download all datasets at once using the command:
                ```bash
                # If you do not have gdown installed, install it first
                # brew install gdown or pip install gdown
                gdown https://drive.google.com/drive/folders/1n-5zkNqT97W-I9Dc7X_mG4kezskfVtlb -O ./data --folder
                ```
        - **Option B:** Manually download specific datasets from the same Google Drive folder on demand.
     - **Channel 2: Official data sources**
         - Follow the data source links provided in the various notebooks.
         - Download the datasets directly from their official channels.
         - Place the downloaded files in the `data/` folder or any other folder of your choice.
    
       Voila! You are ready to go! 🎉

**What you’ll learn**:

- **Assemble** a pipeline to `load`, `process`, `enrich`, and `visualise` `PLUTO` data.
- **Execute** the pipeline efficiently with a single workflow command.
- **Display** an `interactive map` of `average floors per intersection`.

The `UrbanPipeline` class simplifies complex workflows by chaining steps together, enhancing reusability and clarity.
Let’s dive in and see how it works!

## Final Viz

![Final Viz](../public/resources/img_examples/getting_started.png)

## Import & Instantiate an instance of `UrbanMapper`

```python
import urban_mapper as um
from urban_mapper.pipeline import UrbanPipeline

# Initialise UrbanMapper
mapper = um.UrbanMapper()
```

## Step 1: Define the Pipeline

**Goal**: Set up all components of the workflow in a single pipeline.

**Input**: Configurations for each `UrbanMapper` module.

**Output**: An `UrbanPipeline` object ready to process data.

We define each step—urban `layer`, `loader`, `imputer`, `filter`, `enricher`, and `visualiser`—with their specific
roles:

- **Urban Layer**: `Street intersections` in `Downtown Brooklyn`.
- **Loader**: `PLUTO` data from `CSV`.
- **Imputer**: Fills `missing` coordinates.
- **Filter**: `Trims` data to the bounding box.
- **Enricher**: `Adds average floors per intersection`.
- **Visualiser**: Prepares an `interactive map`.

```python
urban_layer = (
    mapper
    .urban_layer
    .with_type("streets_intersections")
    .from_place("Downtown Brooklyn, New York City, USA", network_type="drive")
    .with_mapping(
        longitude_column="longitude",
        latitude_column="latitude",
        output_column="nearest_intersection",
        threshold_distance=50,  # Optional.
    )
    .build()
)

loader = (
    mapper
    .loader
    .from_file("./pluto.csv")
    .with_columns(longitude_column="longitude", latitude_column="latitude")
    .build()
)

imputer = (
    mapper
    .imputer
    .with_type("SimpleGeoImputer")
    .on_columns(longitude_column="longitude", latitude_column="latitude")
    .build()
)

filter_step = mapper.filter.with_type("BoundingBoxFilter").build()

enricher = (
    mapper
    .enricher
    .with_data(group_by="nearest_intersection", values_from="numfloors")
    .aggregate_by(method="mean", output_column="avg_floors")
    .build()
)

visualiser = (
    mapper
    .visual
    .with_type("Interactive")
    .with_style({"tiles": "CartoDB dark_matter", "colorbar_text_color": "white"})
    .build()
)

# Assemble the pipeline
# A step is a tuple of (name, object)
# Note that you can instantiate the object within the pipeline and not before.
# For clarity, we instantiate them before.
pipeline = UrbanPipeline(
    [
        ("urban_layer", urban_layer),  # Step 1
        ("loader", loader),  # Step 2
        ("imputer", imputer),  # Step 3
        ("filter", filter_step),  # Step 4
        ("enricher", enricher),  # Step 5 
        ("visualiser", visualiser),  # Step 6
    ]
)

# Preview the pipeline format ascii
pipeline.preview()
```

## Step 2: Execute the Pipeline

**Goal**: Process the data through all defined steps in one operation.

**Input**: The `UrbanPipeline` object from Step 1.

**Output**: A mapped GeoDataFrame and an enriched `UrbanLayer` with processed data.

The `compose_transform` method runs the entire workflow—`loading` data, `imputing`, `filtering`, `mapping`, and
`enriching`—in a
single call, ensuring seamless data flow.

```python
mapped_data, enriched_layer = pipeline.compose_transform()
```

## Step 3: Visualise Results

**Goal**: Display the enriched data on an interactive map.

**Input**: The enriched layer from Step 2 and columns to display (`avg_floors`).

**Output**: An interactive Folium map showing average floors per intersection.

The pipeline’s `visualise` method leverages the pre-configured visualiser to generate the map directly from the enriched
layer.

```python
fig = pipeline.visualise(["avg_floors"])
fig  # Display the map
```

## Step 4: Save and Load Pipeline

**Goal**: Preserve the pipeline for future use or sharing.

**Input**: A file path (`./my_pipeline.dill`) for saving.

**Output**: A saved pipeline file and a reloaded `UrbanPipeline` object.

Saving with `save` and loading with `load` allows you to reuse or distribute your workflow effortlessly.

```python
# Save the pipeline
pipeline.save("./my_pipeline.dill")

# Load it back
loaded_pipeline = UrbanPipeline.load("./my_pipeline.dill")

# Preview the loaded pipeline
loaded_pipeline.preview()

# Visualise with the loaded pipeline
fig = loaded_pipeline.visualise(["avg_floors"])
```

!!! note "Much more exists in the pipeline!"
    The `UrbanPipeline` class is further flourished with additional methods for looking-through the pipeline,
    exporting, etc. Feel free to explore the API reference.

## Conclusion

Well done! Using `UrbanPipeline`, you’ve efficiently processed and visualised `PLUTO` data with fewer steps and cleaner
code compared to the step-by-step approach. This method shines for its **simplicity** and **reusability**, making it
easy to `save`, `share`, and `rerun` your workflow.

Ready for more? Explore the `examples/` folder for advanced case studies—like analysing taxi trips or urban
collisions—and see how the pipeline can integrate with other tools.

Ready to take it further? Head over to the [# Urban Mapper's Examples](examples.md) section for a
detailed guide on how
to walk through all the realease `UrbanMapper`'s Jupyter notebook examples for urban spatial data analysis.

Cheers!