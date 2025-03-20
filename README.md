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

![UrbanMapper Cover](public/resources/urban_mapper_cover.png)


___

> [!IMPORTANT]
> 1) We highly recommend exploring the `/example` folder for Jupyter Notebook-based examples 🎉
> 2) The following library is under active development and is not yet _stable_. Expect bugs & frequent changes!

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

First, ensure `uv` is installed on your machine by
following [these instructions](https://docs.astral.sh/uv/getting-started/installation/).

### Prerequisites

- Install `uv` as described above.
- Clone `Auctus` (required for alpha development) into the same parent directory as `UrbanMapper`. Use:
  ```bash
  git clone git@github.com:VIDA-NYU/auctus_search.git
  ```
  This step ensures `pyproject.toml` builds `auctus_search` from source during installation, though we plan for
  `auctus_search` to become a PyPi package (`uv add auctus_search` or `pip install auctus_search`) in future releases.

> [!NOTE]  
> Future versions will simplify this process: `auctus_search` will move to PyPi, removing the need for manual cloning,
> and Jupyter extensions will auto-install via `pyproject.toml` configuration.

### Steps

1. Clone the `UrbanMapper` repository:
   ```bash
   git clone https://github.com/yourusername/UrbanMapper.git
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

## 🚀 Getting Started with UrbanMapper

Are you ready to dive into urban data analysis? The simplest approach to get started with UrbanMapper is to look through
the hands-on examples in the 'examples/' directory. These **Jupyter notebooks** walk you through the library's features,
from loading and prepping data to enriching urban layers and visualising the results. Whether you are new to urban data
or an experienced urban planner, these examples will help you realise UrbanMapper's full potential.

The `examples/` directory is organised into two main sections: `Basics/` and `End-to-End/`. Here’s a quick gander at 
what each notebook covers:

<details>
<summary>

# 🧩 **Basics**

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
    focus on `Downtown Brooklyn`. It does not make sense to keep the entire data that is not in `Downtown Brooklyn`, does it ?
    - *What it does*: Applies a `BoundingBoxFilter` to keep only data within `Downtown Brooklyn`.
    Shows that there could be more filter techniques added.

- **[5] enricher.ipynb**: Add valuable insights to your `urban layers` from your `urban data` information.
    - *What it does*: Enriches a `street intersections` layer with `average building floors` from `PLUTO data`.

- **[6] visualiser.ipynb**: Bring your data to life with maps.
    - *What it does*: Creates `static` and `interactive` maps (e.g. dark-themed) of an `enriched urban layer`.

- **[7] urban_pipeline.ipynb**: Streamline your workflow with a pipeline. Save and Share!
    - *What it does*: Builds and runs an `urban pipeline` that `loads`, `processes`, `enriches`, and `visualises`.

- **[8] pipeline_generator.ipynb**: Let an `LLM` suggest a pipeline for you based on your user input.
    - *What it does*: Generates a pipeline from a description (e.g., mapping PLUTO data to intersections) using a given
    `LLM` of interest from those available. For the example we use `gpt-4o`.
</details>

<details>
<summary>

# 🔄 **End-to-End**

</summary>

These notebooks showcase complete workflows, tying all the pieces together.

- **[1] step_by_step.ipynb**: Walk through the `UrbanMapper` workflow manually.
    - *What it does*: `Loads` PLUTO data, creates an intersections `urban layer`, `imputes`, `filters`, `enriches` with 
    average floors, and `visualises` it—all _step-by-step_.

- **[2] pipeline_way.ipynb**: Achieve the same results with an `urban pipeline`.
    - *What it does*: Streamlines the step-by-step workflow into a single `UrbanPipeline`, showcasing efficiency and
      reusability.
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
