# 🥐 Welcome to the Installation guide!

`UrbanMapper` is a Python package designed for urban spatial data analysis. Before you start, you’ll need to setup your environment and install the appropriate packages. `UrbanMapper` requires Python `3.10` or higher.

--- 

## Virtual environment

You should install `UrbanMapper` in a virtual environment to keep things tidy and avoid dependency conflicts. You can set up your environment using [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended), [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html), or a [virtual environment](https://docs.python.org/3/library/venv.html).

=== "Using uv (Recommended)"

    ```bash
    # Optional: install and pin a specific Python version
    uv python install 3.10
    uv python pin 3.10

    # Create and activate a virtual environment using the pinned Python version
    uv venv
    source .venv/bin/activate

    # Install the package from PyPI
    uv pip install urban-mapper
   
    # Launch Jupyter Lab to explore `UrbanMapper` (faster than running Jupyter without uv)
    uv run --with jupyter jupyter lab

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

## Pip

The most straightforward way to install `UrbanMapper` is with pip (works in any environment):
 ```bash
 pip install urban-mapper
 ```
Launch Jupyter Lab to explore `UrbanMapper`:
```bash
jupyter lab
```
---

## Source
Building `UrbanMapper` from source lets you make changes to the code base. To install from the source, refer to the [Project Setup Guide](../CONTRIBUTING.md/#project-setup-guide).

---

## Conclusion

Well done! You’ve just installed `UrbanMapper`. Ready to take it further? 

Head over to the [# Getting Started Step by Step](quick-start_step_by_step.md) section for a step-by-step guide on how 
to use `UrbanMapper` for urban spatial data analysis.

Cheers!