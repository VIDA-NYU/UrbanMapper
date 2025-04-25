# 🥐 Welcome to the Installation guide!

!!! important "Installation Is From Source, Soon To Be Available From PyPI"
    For the time being, `UrbanMapper` is only available from source. We are working on making it available from PyPI 
    soon. The complexity is due to the fact that `UrbanMapper` is meant to be changing a very lot in the coming weeks,
    and we want to make sure that the PyPI version is stable and well-tested before releasing it. Stay tuned for updates!
    In the meantime, you can install it from source using the instructions below and no worries! It is very fast!

`UrbanMapper` is a Python package designed for urban spatial data analysis. This guide provides instructions for
installing `UrbanMapper`, with a focus on using [uv](https://github.com/astral-sh/uv) for efficient dependency management.
`UrbanMapper` requires Python `3.10` or higher.

---

## Prerequisites

Before installing `UrbanMapper`, ensure you have the following:

- **Python `3.10` or higher**
- **uv** (recommended for installation from source)

To install `uv`, follow the instructions on
the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

If you don’t have Python `3.10` or higher / you prefer to be sure, you can install and pin it using uv:

```bash
uv python install 3.10
uv python pin 3.10
```

---

## Installation

To install `UrbanMapper`, start by cloning the repository:

```bash
git clone git@github.com:VIDA-NYU/UrbanMapper.git
# or
# git clone https://github.com/VIDA-NYU/UrbanMapper.git
cd `UrbanMapper`
```

Then, choose your installation method:

=== "Using uv (Recommended)"

    ![UV Proof](https://github.com/astral-sh/uv/assets/1309177/03aa9163-1c79-4a87-a31d-7a9311ed9310#only-dark)

    !!! tip "UV's readings recommendations:"
        - [Python Packaging in Rust](https://astral.sh/blog/uv)
        - [A Year of UV](https://www.bitecode.dev/p/a-year-of-uv-pros-cons-and-should)
        - [UV Is All You Need](https://dev.to/astrojuanlu/python-packaging-is-great-now-uv-is-all-you-need-4i2d)
        - [State of the Art Python 2024](https://4zm.org/2024/10/28/state-of-the-art-python-in-2024.html)
        - [Data Scientist, From School to Work](https://towardsdatascience.com/data-scientist-from-school-to-work-part-i/)

    Using `uv` is the recommended method for installing `UrbanMapper` from source due to its speed and seamless modern dependency management. Follow these steps:

    1. **Lock and sync dependencies**:

    ```bash
    uv lock
    uv sync
    ```

    2. **(Recommended) Install Jupyter extensions** for interactive visualisations requiring Jupyter widgets:

    ```bash
    uv run jupyter labextension install @jupyter-widgets/jupyterlab-manager
    ```

    3. **Launch Jupyter Lab** to explore `UrbanMapper` (faster than running Jupyter without uv):

    ```bash
    uv run --with jupyter jupyter lab
    ```

=== "Using pip"

    If you prefer not to use `uv`, you can install `UrbanMapper` using `pip`. This method is slower and requires more manual intervention.

    **Assumptions**:

    - You have `pip` installed.
    - You are working within a virtual environment or a conda environment.

    !!! note
        If you are not using a virtual or conda environment, it is highly recommended to set one up to avoid conflicts. Refer to [Python's venv documentation](https://docs.python.org/3/library/venv.html) or [conda's environment management guide](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) for assistance.

    1. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    2. **Install `UrbanMapper`**:

    ```bash
    pip install -e ./UrbanMapper
    # or if you ensure you are in your virtual environment, cd UrbanMapper && pip install -e .
    ```

    !!! tip
        The `-e` flag installs `UrbanMapper` in editable mode, allowing changes to the code to be reflected immediately. If you don’t need this, use `pip install ./UrbanMapper` instead.

    3. **(Recommended) Install Jupyter extensions** for interactive visualisations:

    ```bash
    jupyter labextension install @jupyter-widgets/jupyterlab-manager
    ```

    4. **Launch Jupyter Lab**:

    ```bash
    jupyter lab
    ```

---

## Conclusion

Well done! You’ve just downloaded and installed `UrbanMapper`. Ready to take it further? 

Head over to the [# Getting Started Step by Step](quick-start_step_by_step.md) section for a step-by-step guide on how 
to use `UrbanMapper` for urban spatial data analysis.

Cheers!