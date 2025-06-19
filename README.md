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



![UrbanMapper Cover](https://i.imgur.com/hZ2XkrN.png)


___

> [!IMPORTANT]
> - 📹 `UrbanMapper` Introductory Video 👉 https://www.youtube.com/watch?v=QUmfvda_z2U 👈
> - 🤝 We support [JupyterGIS](https://github.com/geojupyter/jupytergis) following one of your `Urban Pipeline`'s analysis for collaborative in real-time exploration on Jupyter 🏂 Shout-out to [@mfisher87](https://github.com/mfisher87) and `JGIS` team for their tremendous help.

## UrbanMapper –– In a Nutshell

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

## Installation

Install `UrbanMapper` via ``pip`` (works in any environment):
 ```bash
 pip install urban-mapper
 ```
Then launch Jupyter Lab to explore `UrbanMapper`:
```bash
jupyter lab
```

> [!TIP]
> We recommend installing `UrbanMapper` in a virtual environment to keep things tidy and avoid dependency conflicts. You can find detailed instructions—including how to install within a virtual environment using [uv](https://docs.astral.sh/uv/getting-started/installation/), [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) or from source—
in the [UrbanMapper Installation Guide](https://urbanmapper.readthedocs.io/en/latest/getting-started/installation/).
> 

---

# Urban Layers Currently Supported

`UrbanMapper` currently supports loading the following urban layers:

- **Street networks** (`roads` and `intersections`) from `OpenStreetMap` via [OSMNx](https://osmnx.readthedocs.io/en/stable/)
- **Pedestrian infrastructure** (`sidewalks` and `crosswalks`) via [`Tile2Net`](https://github.com/VIDA-NYU/tile2net) (automated mapping from aerial imagery)
- **City features** (`buildings`, `parks`, `bike lanes`, etc.) from `OpenStreetMap` via [OSMNx](https://osmnx.readthedocs.io/en/stable/)
- **Administrative boundaries** (`neighborhoods`, `cities`, `states`, `countries`) from `OpenStreetMap` via [OSMNx](https://osmnx.readthedocs.io/en/stable/)

More layers, like `subway`/`tube` networks, will be added in the future. If you have any suggestions, please feel free to
open an issue or a pull request!

# 🚀 Getting Started with UrbanMapper

Are you ready to dive into urban data analysis in a couple of lines of code? The simplest approach to get started with `UrbanMapper` is to look
through the two getting-started examples available in the documentation then walk through the hands-on examples in the 
`examples/` directory. Documentation is available at [UrbanMapper Documentation](https://urbanmapper.readthedocs.io/en/latest/).

---

## Licence

`UrbanMapper` is released under the [MIT Licence](./LICENCE).
