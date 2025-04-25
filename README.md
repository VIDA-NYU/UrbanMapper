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



![UrbanMapper Cover](./docs/public/resources/urban_mapper_cover.png)


___

> [!IMPORTANT]
> 1) Documentation is out ! Check it out [here](https://urbanmapper.readthedocs.io/en/latest/) 🚀
> 3) We support [JupyterGIS](https://github.com/geojupyter/jupytergis) as a bridge to export your `Urban Pipeline` for collaborative exploration 🏂 Shout-out to [@mfisher87](https://github.com/mfisher87) for his tremendous help.

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

Voila 🥐 ! We'd recommend you explore next the # `Getting Started with UrbanMapper` section to see how to use the tool.

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
6) **Region Neighborhoods** –– `UrbanMapper` can load neighborhoods boundaries from `OpenStreetMap` (OSM) using `OSMNx` Features
   module.
7) **Region Cities** –– `UrbanMapper` can load cities boundaries from `OpenStreetMap` (OSM) using `OSMNx` Features module.
8) **Region States** –– `UrbanMapper` can load states boundaries from `OpenStreetMap` (OSM) using `OSMNx` Features module.
9) **Region Countries** –– `UrbanMapper` can load countries boundaries from `OpenStreetMap` (OSM) using `OSMNx`
   Features module.

More will be added in the future, e.g `Subway`/`Tube` networks, etc. If you have any suggestions, please feel free to
open an issue or a pull request on our GitHub repository.

**References**

- [OSMNx](https://osmnx.readthedocs.io/en/stable/) –– [Tile2Net](https://github.com/VIDA-NYU/tile2net) –– [OSM Cities Features](https://wiki.openstreetmap.org/wiki/Map_features)

# 🚀 Getting Started with UrbanMapper

Are you ready to dive into urban data analysis? The simplest approach to get started with `UrbanMapper` is to look
through the two getting-started examples available in the documentation then walk through the hands-on examples in the 
`examples/` directory. These **Jupyter notebooks** walk you through the library's features, from `loading` and 
`prepping data` to `enriching` urban layers and `visualising` the results. 

Documentation is available at [UrbanMapper Documentation](https://urbanmapper.readthedocs.io/en/latest/).

---

## Licence

`UrbanMapper` is released under the [MIT Licence](./LICENCE).
