# How to Install UrbanMapper?

`UrbanMapper` is a Python package designed for urban spatial data analysis. Before you start, you’ll need to setup your environment and install the appropriate packages. `UrbanMapper` requires Python `3.10` or higher.

--- 

## ➡️ Via Virtual environment

We recommend you to install `UrbanMapper` in a virtual environment to keep things tidy and avoid dependency conflicts. You can set up your environment using [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended), [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html), or a [virtual environment](https://docs.python.org/3/library/venv.html).

=== "Using uv (Recommended)"

    ```bash
    # Install the package from PyPI
    uv add urban-mapper
   
    # Launch Jupyter Lab to explore `UrbanMapper` (faster than running Jupyter without uv)
    uv run --with jupyter jupyter lab
    ```
    *Optional: Get into your UV's venv despite not being necessary / recommended by UV*

    ```bash
    #Create and activate a virtual environment using the pinned Python version
    uv venv
    source .venv/bin/activate
    jupyter lab

    # To exit the environment
    deactivate
    ```

=== "Using conda"

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
---

## ➡️ Via `Pip`

The most straightforward way to install `UrbanMapper` is with pip (works in any environment):
 ```bash
 pip install urban-mapper
 ```
Launch Jupyter Lab to explore `UrbanMapper`:
```bash
jupyter lab
```
---

## ➡️ Optional extras (optional modules)

Install optional capabilities on demand:

#### Notebook tooling

```bash
pip install urban-mapper[notebook]
uv add urban-mapper --group notebook
```

#### Interactive table visualisations

```bash
pip install urban-mapper[interactive_table_vis]
uv add urban-mapper --group interactive_table_vis
```

#### Auctus mixins

```bash
pip install urban-mapper[auctus_mixins]
uv add urban-mapper --group auctus_mixins
```

#### Pipeline generators

```bash
pip install urban-mapper[pipeline_generators]
uv add urban-mapper --group pipeline_generators
```

#### JupyterGIS mixins

```bash
pip install urban-mapper[jupytergis_mixins]
uv add urban-mapper --group jupytergis_mixins
```

#### Everything at once

```bash
pip install urban-mapper[full]
uv add urban-mapper --group full
```

## ➡️ From Source (Developer)
Building `UrbanMapper` from source lets you make changes to the code base. To install from the source, refer to the [Project Setup Guide](../CONTRIBUTING.md/#project-setup-guide).
