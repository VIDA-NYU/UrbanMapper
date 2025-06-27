# `UrbanMapper`’s Examples Playground

!!! warning "New here? Start with the basics!"
    Before jumping into this playground, make sure you’ve  walked through
    the [Getting Started Step-By-Step](./getting-started/quick-start_step_by_step.md)
    and [Getting Started W/ Pipeline](./getting-started/quick-start_pipeline.md) guides. They’re explaining quite in depth `UrbanMapper`—trust us,
    it could be useful before delving into these examples, which are more straightforward and focused on specific tasks.

Welcome to the `examples/` folder, where you will get hands-on experience with `UrbanMapper`!  This set of Jupyter
notebooks guides users through the process of loading, mapping, enhancing, and visualising urban data. These examples
are suitable for both newcomers to urban analysis and experienced urban planners seeking to improve their process. 

Explore the full potential of `UrbanMapper` with these real-world demos, including Brooklyn collisions, Paris trees, cab rides,
to name a few.

!!! tip "Where’s the data at?"
    All the datasets powering these examples are public and ready for you to grab. Pick your channel:

    - **Channel 1: Our Google Drive stash**
        - **Option A**: Snag everything in one go with this command (no fuss, no muss!):
            ```bash
            # Need gdown? Install it first: brew install gdown or pip install gdown
            gdown https://drive.google.com/drive/folders/1n-5zkNqT97W-I9Dc7X_mG4kezskfVtlb -O ./data --folder
            ```
        - **Option B**: Cherry-pick what you need manually from the [Google Drive folder](https://drive.google.com/drive/folders/1n-5zkNqT97W-I9Dc7X_mG4kezskfVtlb).
    - **Channel 2: Straight from the source**
        - Check the links in each notebook, download from the official sites, and drop them into your `data/` folder.
    - **Channel 3: HuggingFace OSCUR datasets hub**
        - If you prefer HuggingFace, you can find the datasets in the [OSCUR datasets hub](https://huggingface.co/datasets/oscur).
            Use the `datasets` library to load them directly into your code (integrated with `UrbanMapper`):
            ```python
            import urbanmapper as um
            loader = um.UrbanMapper().loader.from_huggingface("oscur/pluto") # replace "pluto" with the dataset you want.
            gdf = loader.load()
            print(gdf.head()) 
            ```
    
    Once you’ve got the goods, you’re ready to roll! 🎉


## Interactivity Table Support

!!! important "Some Notebooks Are Fully Interactive / Partially Interactive / Non-interactive"
    - **Fully Interactive**: These notebooks are fully interactive, meaning you can view the entire process from input to output directly on the documentation site.
    - **Partially Interactive**: These notebooks are partially interactive; while most content is visible, some components, such as maps, may not display because Material For MkDocs does not support some of Ipywidget components used in some Jupyter notebooks. However, you can find these notebooks in the `examples/` directory of the original repository and run them locally to view the full content.
    - **Non-interactive**: These are static notebooks that have not been executed, often because they require data or resources that were not available. For example, if certain data are needed but were not accessible on HuggingFace, we could not retrieve them. For these notebooks, we suggest cloning the repository, installing the library, and running them locally too.
    
    All the notebooks mentioned can be found in the `examples/` directory of the original repository. 
    For the partially interactive and non-interactive notebooks, running them locally will allow you to experience 
    their full functionality.
    
    See below the table 👇

| Category                   | Fully Interactive                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Partially Interactive                                                                                                       | Non-interactive                                                                                                           | Comments                                                                                                                                                                                                            |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1-Per-Module**           | <ul><li><a href="../copy_of_examples/1-Per-Module/3-imputer">Imputer</a></li><li><a href="../copy_of_examples/1-Per-Module/4-filter">Filter</a></li><li><a href="../copy_of_examples/1-Per-Module/5-enricher">Enricher</a></li><li><a href="../copy_of_examples/1-Per-Module/6-visualiser">Visualiser</a></li><li><a href="../copy_of_examples/1-Per-Module/7-urban_pipeline">Urban Pipeline</a></li></ul> | <ul><li><a href="../copy_of_examples/1-Per-Module/2-urban_layer">Urban Layer</a></li></ul>                              | <ul><li><a href="../copy_of_examples/1-Per-Module/1-loader">Loader</a></li><li><a href="../copy_of_examples/1-Per-Module/8-pipeline_generator">Pipeline Generator</a></li></ul> | - Non-interactive: Require specific data or setup not available in the documentation environment.<br>- Partially interactive: Some cells require local files not available on HuggingFace or others. |
| **2-End-to-End**           | <ul><li><a href="../copy_of_examples/2-End-to-End/1-step_by_step">Step by Step</a></li><li><a href="../copy_of_examples/2-End-to-End/2-pipeline_way">Pipeline Way</a></li></ul>                                                                                                                                                                                                                                                  |                                                                                                                           |                                                                                                                           |                                                                                                                                                                                                                     |
| **3-Case-Studies**         | <ul><li><a href="../copy_of_examples/3-Case-Studies/1-Downtown-BK-Collisions/1-Downtown_BK_Collisions_StepByStep">Downtown BK Collisions - Step by Step</a></li><li><a href="../copy_of_examples/3-Case-Studies/1-Downtown-BK-Collisions/2-Downtown_BK_Collisions_Pipeline">Downtown BK Collisions - Pipeline</a></li></ul> | <ul><li><a href="../copy_of_examples/3-Case-Studies/2-Downtown-BK-Taxi-Trips/1-Downtown_BK_Taxi_Trips_StepByStep">Downtown BK Taxi Trips - Step by Step</a></li><li><a href="../copy_of_examples/3-Case-Studies/2-Downtown-BK-Taxi-Trips/2-Downtown_BK_Taxi_Trips_Pipeline">Downtown BK Taxi Trips - Pipeline</a></li></ul> | <ul><li><a href="../copy_of_examples/3-Case-Studies/3-Europe-Restaurants/1-EU_Restaurants_Pipeline">EU Restaurants Pipeline</a></li><li><a href="../copy_of_examples/3-Case-Studies/4-Paris-Remarkable-Trees/1-Paris_Remarquable_Trees_Pipeline">Paris Remarkable Trees - Pipeline</a></li><li><a href="../copy_of_examples/3-Case-Studies/5-Overture-instead-of-OSM/1-overture_pipeline">Overture Pipeline</a></li><li><a href="../copy_of_examples/3-Case-Studies/1-Downtown-BK-Collisions/3-Downtown_BK_Collisions_Advanced_Pipeline">Downtown BK Collisions - Advanced Pipeline</a></li><li><a href="../copy_of_examples/3-Case-Studies/1-Downtown-BK-Collisions/4-Downtown_BK_Collisions_Advanced_Pipeline_Extras">Downtown BK Collisions - Advanced Pipeline Extras</a></li><li><a href="../copy_of_examples/3-Case-Studies/2-Downtown-BK-Taxi-Trips/3-Downtown_BK_Taxi_Trips_Advanced_Pipeline">Downtown BK Taxi Trips - Advanced Pipeline</a></li><li><a href="../copy_of_examples/3-Case-Studies/2-Downtown-BK-Taxi-Trips/4-Downtown_BK_Taxi_Trips_Advanced_Pipeline_Extras">Downtown BK Taxi Trips - Advanced Pipeline Extras</a></li><li><a href="../copy_of_examples/3-Case-Studies/4-Paris-Remarkable-Trees/2-Paris_Remarquable_Trees_Advanced_Pipeline">Paris Remarkable Trees - Advanced Pipeline</a></li><li><a href="../copy_of_examples/3-Case-Studies/5-Overture-instead-of-OSM/2-overture_pipeline_advanced">Advanced Overture Pipeline</a></li></ul> | - EU Restaurants, Paris Remarkable Trees - Pipeline, Overture Pipeline: Require specific data not available on HuggingFace.<br>- All Advanced Pipelines: Too resource-intensive to run in documentation or locally.<br>- Partially interactive items require ipywidgets, which are not supported by material for mkdocs. |
| **4-External-Libraries-Usages** | <ul><li><a href="../copy_of_examples/4-External-Libraries-Usages/2-interactive_table_vis">Interactive Table VIS</a></li></ul>                                                                                                                                                                                                                                                                                                                                                              |                                                                                                                           | <ul><li><a href="../copy_of_examples/4-External-Libraries-Usages/1-auctus_search">Auctus Search</a></li><li><a href="../copy_of_examples/4-External-Libraries-Usages/3-jupyter_gis_multi_pipeline/1-one_pipeline">Jupyter GIS Multi Pipeline - One Pipeline</a></li><li><a href="../copy_of_examples/4-External-Libraries-Usages/3-jupyter_gis_multi_pipeline/2-two_pipeline">Jupyter GIS Multi Pipeline - Two Pipeline</a></li><li><a href="../copy_of_examples/4-External-Libraries-Usages/3-jupyter_gis_multi_pipeline/3-three_pipeline">Jupyter GIS Multi Pipeline - Three Pipeline</a></li></ul> | Non-interactive due to requiring external resources or specific data not accessible in the documentation environment.  Furthermore, JGIS is not yet supported in material for MKDocs.                               |