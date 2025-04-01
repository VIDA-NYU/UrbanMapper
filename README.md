<div align="center">
   <h1>UrbanMapper</h1>
   <h3>Enrich Urban Layers Given Urban Datasets</h3>
   <p><i>with ease-of-use API and Sklearn-alike Shareable & Reproducible Urban Pipeline</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Beartype&message=compliant&color=4CAF50&style=for-the-badge&logo=https://avatars.githubusercontent.com/u/63089855?s=48&v=4&logoColor=white" alt="Beartype compliant">
      <img src="https://img.shields.io/static/v1?label=UV&message=compliant&color=2196F3&style=for-the-badge&logo=UV&logoColor=white" alt="UV compliant">
      <img src="https://img.shields.io/static/v1?label=RUFF&message=compliant&color=9C27B0&style=for-the-badge&logo=RUFF&logoColor=white" alt="RUFF compliant">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
      <img src="https://img.shields.io/github/actions/workflow/status/VIDA-NYU/UrbanMapper/compile.yaml?style=for-the-badge&label=Compilation&logo=githubactions&logoColor=white" alt="Compilation Status">
   </p>
</div>



![UrbanMapper Cover](public/resources/urban_mapper_cover.png)


___

> [!IMPORTANT]
> 1) We support [JupyterGIS](https://github.com/geojupyter/jupytergis) as a bridge to export your Urban Pipeline for collaborative exploration 🏂 Shout-out to [@mfisher87](https://github.com/mfisher87) for his tremendous help.
> 2) We highly recommend exploring the `/example` folder for Jupyter Notebook-based examples 🎉
> 3) The following library is under active development and is not yet _stable_. Expect bugs & frequent changes!

## 🌆 UrbanMapper –– In a Nutshell

`UrbanMapper` –– `f(.)` –– brings urban layers (e.g. `Street Roads` / `Intersections` or `Sidewalks` / `Cross Walks`) ––
`X` ––
and your urban datasets –– `Y` –– together through the function *f(X, Y) = X ⋈ Y*, allowing you to spatial-join
these components, and enrich `X` given `Y` attributes, features and information.

While `UrbanMapper` is built with a **Scikit-Learn-like philosophy** – i.e., (I) from `loading` to `viz.` passing by
`mapping` and `enriching`, we want to cover as much as users’ wishes in a welcoming way without having to code 20+/50+
lines of code for one, ~~non-reproducible, non-shareable, non-updatable piece of code;~~ and (II) the library’s
flexibility allows for easy
contributions to sub-modules without having to start from scratch _“all the time”_.

This means that `UrbanMapper` is allowing you to build a reproducible, shareable, and updatable urban pipeline in a
few lines of code 🎉 This could therefore be seen as a stepping-stone / accelerator to further analysis such as machine
learning-based ones.

The only thing we request from you is to be sure that your datasets `Y` are spatial datasets (i.e. with latitude and
longitude coordinates) and let's
urban proceed with enriching your urban layer of interests from **insights**  your _datasets_ comes with.

---

## 🥐 Installation

We *highly* recommend using `uv` for installation from source to avoid the hassle of `Conda` or other package managers.
It is also the fastest known to date on the OSS market and manages dependencies seamlessly without manual environment
activation (Biggest flex!). If you do not want to use `uv`, there are no issues, but we will cover it in the upcoming
documentation – not as follows.

> [!TIP]
> **UV's readings recommendations:**
> - [Python Packaging in Rust](https://astral.sh/blog/uv)
> - [A Year of UV](https://www.bitecode.dev/p/a-year-of-uv-pros-cons-and-should)
> - [UV Is All You Need](https://dev.to/astrojuanlu/python-packaging-is-great-now-uv-is-all-you-need-4i2d)
> - [State of the Art Python 2024](https://4zm.org/2024/10/28/state-of-the-art-python-in-2024.html)
> - [Data Scientist, From School to Work](https://towardsdatascience.com/data-scientist-from-school-to-work-part-i/)

### Prerequisites

- First, ensure `uv` is installed on your machine by
following [these instructions](https://docs.astral.sh/uv/getting-started/installation/).

- Second, make sure you install at least `python` 3.10+. If you are not sure:

```bash
uv python install 3.10
uv python pin 3.10
```

And you are ready to go! 🎉

### Steps

1. Clone the `UrbanMapper` repository:
   ```bash
   git clone git@github.com:VIDA-NYU/UrbanMapper.git
   # git clone https://github.com/VIDA-NYU/UrbanMapper.git
   cd UrbanMapper
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
4. Launch Jupyter Lab to explore `UrbanMapper` (Way faster than running Jupyter without `uv`):
   ```bash
   uv run --with jupyter jupyter lab
   ```

Voila 🥐 ! You’re all set to explore `UrbanMapper` in Jupyter Lab.

<details>

<summary>
🫣 Different ways to install UrbanMapper (e.g w/ pip)
</summary>

<br>

> **Note on Alternative Dependency Management Methods**
>
> While we strongly recommend using `uv` for managing dependencies due to its superior speed and ease of use, 
> alternative methods are available for those who prefer not to use `uv`. These alternatives are not as efficient, 
> as they are slower and require more manual intervention.
>
> Please be aware that the following assumptions are made for these alternative methods:
> - You have `pip` installed.
> - You are working within a virtual environment or a conda environment.
>
> If you are not currently using a virtual or conda environment, we highly recommend setting one up to prevent 
> potential conflicts and maintain a clean development workspace. For assistance, refer to the following resources:
> - [Creating a Python virtual environment](https://docs.python.org/3/library/venv.html)
> - [Managing conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

1. Clone the `UrbanMapper` repository:
   ```bash
    git clone git@github.com:VIDA-NYU/UrbanMapper.git
    # git clone https://github.com/VIDA-NYU/UrbanMapper.git
    cd UrbanMapper
   ```
2. Install `UrbanMapper` dependencies using `pip`:
   ```bash
    pip install -r requirements.txt
   ```
   
3. Install `UrbanMapper`:
   ```bash
    pip install -e ./UrbanMapper
    # or if you ensure you are in your virtual environment, cd UrbanMapper && pip install -e .
    # Note that -e means "editable" mode, which allows you to make changes to the code and see them reflected.
    # If you don't want to use editable mode, you can just run pip install ./UrbanMapper
    ```
   
4. (Recommended) Install Jupyter extensions for interactive visualisations requiring Jupyter widgets:
   ```bash
    jupyter labextension install @jupyter-widgets/jupyterlab-manager
   ```

5. Launch Jupyter Lab to explore `UrbanMapper`:
   ```bash
    jupyter lab
   ```
   
</details>

# 🗺️ Urban Layers Currently Supported

`UrbanMapper` currently supports the following urban layers:

1) **Streets Roads** –– `UrbanMapper` can load street road networks from `OpenStreetMap` (OSM) using `OSMNx`.
2) **Streets Intersections** –– `UrbanMapper` can load street intersections from `OpenStreetMap` (OSM) using `OSMNx`.
3) **Sidewalks** –– `UrbanMapper` can load sidewalk via `Tile2Net` using Deep Learning for automated mapping of
   pedestrian infrastructure from aerial imagery.
4) **Cross Walks** –– `UrbanMapper` can load crosswalk via `Tile2Net` using Deep Learning for automated mapping of
   pedestrian infrastructure from aerial imagery.
5) **Cities' Features** -- `Urban Mapper` can load OSM cities features such as buildings, parks, Bike Lanes etc. via
   `OSMNx` API.

More will be added in the future, e.g `Subway`/`Tube` networks, `States`/`Provinces`, `Countries`/
`Regions`, `Continents`, etc.

**References**

- [OSMNx](https://osmnx.readthedocs.io/en/stable/) –– [Tile2Net](https://github.com/VIDA-NYU/tile2net) –– [OSM Cities Features](https://wiki.openstreetmap.org/wiki/Map_features)

# 🚀 Getting Started with UrbanMapper

Are you ready to dive into urban data analysis? The simplest approach to get started with `UrbanMapper` is to look
through
the hands-on examples in the `examples/` directory. These **Jupyter notebooks** walk you through the library's features,
from loading and prepping data to enriching urban layers and visualising the results. Whether you are new to urban data
or an experienced urban planner, these examples will help you realise `UrbanMapper`'s full potential.

The `examples/` directory is organised into three main sections: `Basics/`, `End-to-End/`, `Study Cases` and
`External Libraries Usages`. Here’s a quick gander at what each notebook covers:

<details>
<summary>

### 🧩 **Basics**

</summary>

- **[1] loader.ipynb**: Learn how to `load urban data` from various formats into `UrbanMapper`.
    - *What it does*: Demonstrates loading PLUTO (CSV), taxi trip (Parquet), and NYC Pluto buildings information
      (Shapefile) data, setting the stage for analysis.

- **[2] urban_layer.ipynb**: Discover how to create `urban layers` like `streets` or `intersections`.
    - *What it does*: Builds a streets layer for `Downtown Brooklyn` and previews it statically.

- **[3] imputer.ipynb**: Handle missing geospatial data with ease.
    - *What it does*: Uses `SimpleGeoImputer` to fill in missing coordinates in PLUTO data.
      Shows that there are more imputer techniques available and that more could be implemented.

- **[4] filter.ipynb**: Focus your data on specific areas. Usecase: You have data for the entire _Big Apple_, but you
  focus on `Downtown Brooklyn`. It does not make sense to keep the entire data that is not in `Downtown Brooklyn`, does
  it ?
    - *What it does*: Applies a `BoundingBoxFilter` to keep only data within `Downtown Brooklyn`.
      Shows that there could be more filter techniques added.

- **[5] enricher.ipynb**: Add valuable insights to your `urban layers` from your `urban data` information.
    - *What it does*: Enriches a `street intersections` layer with `average building floors` from `PLUTO data`.

- **[6] visualiser.ipynb**: Bring your data to life with maps.
    - *What it does*: Creates `static` and `interactive` maps (e.g. dark-themed) of an `enriched urban layer`.

- **[7] urban_pipeline.ipynb**: Streamline your workflow with a pipeline. Save and Share!
    - *What it does*: Builds and runs an `urban pipeline` that `loads`, `processes`, `enriches`, and `visualises`.
    - *Beyond*: It shows how to `save` and `load` your pipeline for future use such as e.g ML-exploration, as one is being showcased.
    - *Bonus*: We also show how to export your urban pipeline to [JupyterGIS](https://github.com/geojupyter/jupytergis).

- **[8] pipeline_generator.ipynb**: Let an `LLM` suggest a pipeline for you based on your user input.
    - *What it does*: Generates a pipeline from a description (e.g., mapping PLUTO data to intersections) using a given
      `LLM` of interest from those available. For the example we use `gpt-4o`.

</details>

<details>
<summary>

### 🔄 **End-to-End**

</summary>

These notebooks showcase complete workflows, tying all the pieces together.

- **[1] step_by_step.ipynb**: Walk through the `UrbanMapper` workflow manually.
    - *What it does*: `Loads` PLUTO data, creates an intersections `urban layer`, `imputes`, `filters`, `enriches` with
      average floors, and `visualises` it—all _step-by-step_.

- **[2] pipeline_way.ipynb**: Achieve the same results with an `urban pipeline`.
    - *What it does*: Streamlines the step-by-step workflow into a single `UrbanPipeline`, showcasing efficiency and
      reusability.

</details>


<details>
<summary>

### 📊 **Study Cases**

</summary>

Ready to see `UrbanMapper` tackle real urban challenges? These study cases apply the library to specific datasets,
showing its power in action.

#### 🚗 **Downtown BK Collisions Study**

- **[1] Downtown_BK_Collisions_StepByStep.ipynb**: Get hands-on with collision data analysis.
    - *What it does*: Step-by-step, you’ll load collision data, build an intersections layer, handle missing
      coordinates, filter to Downtown Brooklyn, map collisions to intersections, count them up, and visualize the
      hotspots.

- **[2] Downtown_BK_Collisions_Pipeline.ipynb**: Simplify the process with a pipeline.
    - *What it does*: Wraps the entire workflow into an `UrbanPipeline`, making it a breeze to run and reuse.

- **[3] Downtown_BK_Collisions_Advanced_Pipeline.ipynb**: Take it up a notch with extra metrics.
    - *What it does*: Adds total injuries and fatalities per intersection to the analysis, giving you a fuller picture
      of collision impacts.

- **[4] Downtown_BK_Collisions_Advanced_Pipeline_Extras.ipynb**: Get more insights with additional enrichments than [3].
    - *What it does*: Adds more metrics than [3] by using the custom function from the enricher module allowing us more
      flexibility but needed more coding.


#### 🚖 **Downtown BK Taxi Trips Study**

- **[1] Downtown_BK_Taxi_Trips_StepByStep.ipynb**: Dive into taxi trip data analysis.
    - *What it does*: Manually load taxi data, create a streets layer, impute missing coordinates, filter to the area,
      map pickups and dropoffs to streets, count them, and visualize the busiest spots.

- **[2] Downtown_BK_Taxi_Trips_Pipeline.ipynb**: Streamline your taxi trip analysis.
    - *What it does*: Bundles all the steps into an `UrbanPipeline`, saving you time and effort.

- **[3] Downtown_BK_Taxi_Trips_Advanced_Pipeline.ipynb**: Get more insights with additional enrichments.
    - *What it does*: Adds average fare amount per pickup segment, helping you understand not just where taxis go, but
      how much they earn.

- **[4] Downtown_BK_Collisions_Advanced_Pipeline_Extras.ipynb**: Get more insights with additional enrichments than [3].
    - *What it does*: Adds more metrics than [3] by using the custom function from the enricher module allowing us more
      flexibility but needed more coding.

</details>

<details>
<summary>

### 🔗 **External Libraries Usage**

</summary>

UrbanMapper doesn’t work in isolation—it plays nicely with other powerful tools to make your user journey experience
even more pleasing. To showcase these integrations, we’ve prepared a few notebooks that demonstrate how to use the
mixins that bridge UrbanMapper with other libraries.

- **[1] auctus_search.ipynb**: Find and load datasets with `Auctus` from https://auctus.vida-nyu.org/.
    - *What it does*: Demonstrates searching for urban datasets (like PLUTO) using `Auctus`, a data discovery tool. You’ll
      learn to profile datasets and load them directly into UrbanMapper for analysis.
    See further in https://github.com/VIDA-NYU/auctus_search.

- **[2] interactive_table_vis.ipynb**: Visualise data interactively with `Skrub` from https://skrub-data.org/.
    - *What it does*: Loads a CSV file and uses Skrub’s interactive table visualisation to explore the data. This
      integration allows you to sort, filter, and inspect your urban datasets dynamically.

</details>

---

## 🗺️ Roadmap / Future Work

> [!NOTE]  
> For more about future works, explore the `issues` tab above!

## 🌁 API

> [!IMPORTANT]  
> Full documentation is forthcoming; Hence, expect some breaking changes in the API – Bare wth us a doc is cooking-up!
> ⚠️

---

## Licence

`UrbanMapper` is released under the [MIT Licence](./LICENCE).
