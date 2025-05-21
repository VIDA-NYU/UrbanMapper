<div align="center">
   <h1>UrbanMapper</h1>
   <h3>Enrich Urban Layers Given Urban Datasets</h3>
   <p><i>with ease-of-use API and Sklearn-alike Shareable & Reproducible Urban Pipeline</i></p>
   <p>
      <img src="https://img.shields.io/pypi/v/urban-mapper?label=Version&style=for-the-badge" alt="PyPI Version">
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
`UrbanMapper` is a Python package designed for urban spatial data analysis. Before you start, you’ll need to setup your environment and install the appropriate packages. `UrbanMapper` requires Python `3.10` or higher. 

For more detailed installation instructions, refer to the [UrbanMapper Documentation](https://urbanmapper.readthedocs.io/en/latest/getting-started/installation/).

### Virtual environment

You should install `UrbanMapper` in a virtual environment to keep things tidy and avoid dependency conflicts. You can set up your environment using [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended), [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html), or a [virtual environment](https://docs.python.org/3/library/venv.html).
Using ``uv`` is the recommended method due to its speed and seamless modern dependency management.

<strong>Using uv (Recommended)</strong>
```bash
# Optional: install and pin a specific Python version
uv python install 3.10
uv python pin 3.10

# Create and activate a virtual env using the pinned Python version
uv venv
source .venv/bin/activate

# Install the package from PyPI
uv pip install urban-mapper

# Launch Jupyter Lab to explore `UrbanMapper`
uv run --with jupyter jupyter lab

# To exit the environment
deactivate
```
<details>
<summary><strong>Using conda</strong></summary>

```bash
# Create and activate a conda environment
conda create -n umenv python=3.10
conda activate umenv

# Install the package from PyPI
pip install urban-mapper

# Launch Jupyter Lab to explore `UrbanMapper`
jupyter lab

# To exit the environment
conda deactivate
```
</details>

### Pip

The most straightforward way to install `UrbanMapper` is with pip (works in any environment):
 ```bash
 pip install urban-mapper
 ```
Launch Jupyter Lab to explore `UrbanMapper`:
```bash
jupyter lab
```
### Source
Building `UrbanMapper` from source lets you make changes to the code base. To install from the source, refer to the [Project Setup Guide](../CONTRIBUTING.md/#project-setup-guide).

---

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
