# 🌇 `Getting Started Examples` guide!

!!! warning "Have you walked through Step-By-Step and the Pipeline guides?"
    Make sure to have walked through the first and second entry points out of how to get started with `UrbanMapper` 
    before diving into this one.

The simplest approach to get to to know more how to work with `UrbanMapper` is to look
through the hands-on examples in the `examples/` directory. These **Jupyter notebooks** walk you through the library's 
features, from `loading` and `prepping data` to `enriching` urban layers and `visualising` the results. 

Whether you are new to urban data or an experienced urban planner, these examples will help you realise 
`UrbanMapper`'s full potential. Whether you are new to urban data science or an experienced data scientist, these 
examples will help you accelerate your urban data science workflow.

!!! tip "We use real open-based data throughout all of our examples, want to know where to get them?"
    You also can download the public datasets used throughout all examples one via two channels.
    
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

## `UrbanMapper` Examples Explained

The `examples/` directory is organised into three main sections: `Basics/`, `End-to-End/`, `Study Cases` and
`External Libraries Usages`. Here’s a quick gander at what each notebook covers:

!!! question "Where to find the examples?"
    The examples are located in the `examples/` directory of the `UrbanMapper` repository.

    [Open Examples :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/tree/main/examples){ .md-button }

=== "🧩 Basics"

    `UrbanMapper` is designed to be intuitive and user-friendly, making it easy to get started with urban data analysis.
     Therefore, the `Basics/` section is your go-to place for learning the various components of `UrbanMapper` and how 
    to use them individually effectively.

    - **[1] loader.ipynb**: Learn how to `load urban data` from various formats into `UrbanMapper`.
        - *What it does*: Demonstrates loading PLUTO (CSV), taxi trip (Parquet), and NYC Pluto buildings information (Shapefile) data, setting the stage for analysis.

    - **[2] urban_layer.ipynb**: Discover how to create `urban layers` like `streets` or `intersections` and more!
        - *What it does*: Builds a streets layer for `Downtown Brooklyn` and previews it statically. Does show more urban layers primitives and show them mostly statically, some interactively.

    - **[3] imputer.ipynb**: Handle missing geospatial data with ease.
        - *What it does*: Uses `SimpleGeoImputer` to fill in missing coordinates in PLUTO data. Shows that there are more imputer techniques available and that more could be implemented.

    - **[4] filter.ipynb**: Focus your data on specific areas. Usecase: You have data for the entire _Big Apple_, but you focus on `Downtown Brooklyn`. It does not make sense to keep the entire data that is not in `Downtown Brooklyn`, does it?
        - *What it does*: Applies a `BoundingBoxFilter` to keep only data within `Downtown Brooklyn`. Shows that there could be more filter techniques added.

    - **[5] enricher.ipynb**: Add valuable insights to your `urban layers` from your `urban data` information.
        - *What it does*: Enriches a `street intersections` layer with `average building floors` from `PLUTO data`.

    - **[6] visualiser.ipynb**: Bring your data to life with maps.
        - *What it does*: Creates `static` and `interactive` maps (e.g., dark-themed) of an `enriched urban layer`.

    - **[7] urban_pipeline.ipynb**: Streamline your workflow with a pipeline. Save and Share!
        - *What it does*: Builds and runs an `urban pipeline` that `loads`, `processes`, `enriches`, and `visualises`.
        - *Beyond*: It shows how to `save` and `load` your pipeline for future use such as e.g., ML-exploration, as one is being showcased.
        - *Bonus*: We also show how to export your urban pipeline to [JupyterGIS](https://github.com/geojupyter/jupytergis).

    - **[8] pipeline_generator.ipynb**: Let an `LLM` suggest a pipeline for you based on your user input.
        - *What it does*: Generates a pipeline from a description (e.g., mapping PLUTO data to intersections) using a given `LLM` of interest from those available. For the example, we use `gpt-4o`.

=== "🔄 End-to-End"

    `UrbanMapper` is all about making your urban data analysis journey smooth and efficient. 
    The `End-to-End/` section showcases how to use `UrbanMapper` to tackle real-world urban data challenges, 
    from loading and processing data to enriching and visualising it, all in an end-to-end manner.

    - **[1] step_by_step.ipynb**: Walk through the `UrbanMapper` workflow manually.
        - *What it does*: `Loads` PLUTO data, creates an intersections `urban layer`, `imputes`, `filters`, `enriches` with average floors, and `visualises` it—all _step-by-step_.

    - **[2] pipeline_way.ipynb**: Achieve the same results with an `urban pipeline`.
        - *What it does*: Streamlines the step-by-step workflow into a single `UrbanPipeline`, showcasing efficiency and reusability.

=== "📊 Study Cases"

    While we have provided a few examples of how to use `UrbanMapper` in the `Basics/` and `End-to-End/` sections,
    there are no better ways to learn than by diving into real-world case studies we have prepared for you.

    🚗 **Downtown BK Collisions Study**

    - **[1] Downtown_BK_Collisions_StepByStep.ipynb**: Get hands-on with collision data analysis.
        - *What it does*: Step-by-step, you’ll load collision data, build an intersections layer, handle missing coordinates, filter to Downtown Brooklyn, map collisions to intersections, count them up, and visualise the hotspots.

    - **[2] Downtown_BK_Collisions_Pipeline.ipynb**: Simplify the process with a pipeline.
        - *What it does*: Wraps the entire workflow into an `UrbanPipeline`, making it a breeze to run and reuse.

    - **[3] Downtown_BK_Collisions_Advanced_Pipeline.ipynb**: Take it up a notch with extra metrics.
        - *What it does*: Adds total injuries and fatalities per intersection to the analysis, giving you a fuller picture of collision impacts.

    - **[4] Downtown_BK_Collisions_Advanced_Pipeline_Extras.ipynb**: Get more insights with additional enrichments than [3].
        - *What it does*: Adds more metrics than [3] by using the custom function from the enricher module allowing us more flexibility but needed more coding.

    🚖 **Downtown BK Taxi Trips Study**

    - **[1] Downtown_BK_Taxi_Trips_StepByStep.ipynb**: Dive into taxi trip data analysis.
        - *What it does*: Manually load taxi data, create a streets layer, impute missing coordinates, filter to the area, map pickups and dropoffs to streets, count them, and visualise the busiest spots.

    - **[2] Downtown_BK_Taxi_Trips_Pipeline.ipynb**: Streamline your taxi trip analysis.
        - *What it does*: Bundles all the steps into an `UrbanPipeline`, saving you time and effort.

    - **[3] Downtown_BK_Taxi_Trips_Advanced_Pipeline.ipynb**: Get more insights with additional enrichments.
        - *What it does*: Adds average fare amount per pickup segment, helping you understand not just where taxis go, but how much they earn.

    - **[4] Downtown_BK_Collisions_Advanced_Pipeline_Extras.ipynb**: Get more insights with additional enrichments than [3].
        - *What it does*: Adds more metrics than [3] by using the custom function from the enricher module allowing us more flexibility but needed more coding.

    🌳 **Remarkable Trees Paris Study**

    - **[1] Paris_Remarquable_Trees_Pipeline.ipynb**: Explore the remarkable trees of Paris within its neighborhoods.
        - *What it does*: This notebook demonstrates how to load the remarkable trees dataset, create a neighborhoods layer, and enrich the neighborhoods with remarkable trees information. E.g., the count of them per neighborhood. Another one may be the circumference of the trees on average per neighborhood. Etc.

    - **[2] Paris_Remarquable_Trees_Advanced_Pipeline.ipynb**: Explore the remarkable trees of Paris within its neighborhoods.
        - *What it does*: This notebook demonstrates how to load the remarkable trees dataset, create a neighborhoods layer, and enrich the neighborhoods with remarkable trees information. E.g., the count of them per neighborhood. Another one may be the circumference of the trees on average per neighborhood. Etc. As an extra, it LLM-compute a summary of why the trees are remarkable and what is the impact of them on the neighborhoods.

=== "🔗 External Libraries Usage"

    `UrbanMapper` doesn’t work in isolation—it plays nicely with other powerful tools to make your user journey experience
    even more pleasing. To showcase these integrations, we’ve prepared a few notebooks that demonstrate how to use the mixins that bridge `UrbanMapper` with other libraries.

    - **[1] auctus_search.ipynb**: Find and load datasets with `Auctus` from https://auctus.vida-nyu.org/.
        - *What it does*: Demonstrates searching for urban datasets (like PLUTO) using `Auctus`, a data discovery tool. You’ll learn to profile datasets and load them directly into `UrbanMapper` for analysis. See further in https://github.com/VIDA-NYU/auctus_search.

    - **[2] interactive_table_vis.ipynb**: Visualise data interactively with `Skrub` from https://skrub-data.org/.
        - *What it does*: Loads a CSV file and uses Skrub’s interactive table visualisation to explore the data. This integration allows you to sort, filter, and inspect your urban datasets dynamically.

    - **[3] Multi Urban Pipeline via Jupyter GIS**: Combines collisions, taxi trips, and 311 NYC sidewalk inquiries for a holistic view of urban dynamics. It showcases `UrbanMapper`’s capability to handle multiple urban pipeline and visualise them on a single interactive and shareable collaborative map. This comprehensive approach allows for a deeper understanding of urban interactions, potentially uncovering correlations between traffic incidents, taxi usage, and public concerns.