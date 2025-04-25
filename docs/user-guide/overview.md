# 🌇 Welcome to the `UrbanMapper` User-Guide!

In this guide, we will walk you though (1) the overall architecture of `UrbanMapper`.  (2) `UrbanMapper` components and (3) framework
modules/mixins. Note that this guide does not cover all the features and capabilities of `UrbanMapper`, but it provides a good overview of how to get started
and what you can do with it. For technical information, please see the `API` reference section.

This guide is not intended to be technically comprehensive. Instead, it will demonstrate hands-on how to use `UrbanMapper`
and its modules and mixins.

## 🏙️ Architecture: In a Nutshell

`UrbanMapper` is built with a modular structure that feels like a well-planned city—each part has its purpose, working
together to make urban analysis straightforward and powerful. Here’s a look at how it all fits.

### 🏗️ Components: The Core Tools

- **Urban Layers**: The groundwork of your analysis—think of them as the `streets roads`, `intersections`, and `neighborhoods` where
  your data takes shape.

- **Modules**: The built-in tools that do the heavy lifting:
    - **Loaders**: Grab your geospatial data and get it ready, much like surveyors plotting out a site.
    - **Imputers**: Fill in any missing coordinates, ensuring your dataset is solid and complete.
    - **Filters**: Narrow your focus to the areas that matter, cutting out the noise.
    - **Enrichers**: Add richer details—like demographics or feature counts—to bring context to your layers.
    - **Visualisers**: Turn your data into clear, compelling `maps` and `charts`.
- **Pipeline**: The organisers that keep everything on track in one smooth vector.
    - **Urban Pipeline**: Stacks your `modules` into a smooth, repeatable and shareable workflow.
    - **Pipeline Generators**: Use `LLM` to build `urban pipelines` from simple instructions.

### 🔗 Mixins: Boosting Power with External Help

Mixins extend `UrbanMapper` by tapping into external libraries and APIs, adding specialised features like:

- **Interactive Visualisations**: Explore your data dynamically with [Skrub](https://skrub-data.org/) rather than the basic Pandas dataframe viz.
- **JupyterGIS Integration**: Work in a collaborative-in-real-time session on maps throughout Jupyter using [JupyterGIS](https://github.com/geojupyter/jupytergis).
- **Auctus Search**: Quickly find datasets with [Auctus](https://auctus.vida-nyu.org/).

Looking ahead, imagine a mixin connecting to a `data lake API`—pulling in data faster than `Auctus Search`, which depends on
manual steps like `searching` and `selecting`. More mixins are in the works, so `UrbanMapper`’s toolkit will keep expanding!

!!! tips "Modules vs. Mixins: What’s the Difference?"
      - **Modules** are `UrbanMapper`’s homegrown tools—the core pieces built from scratch to handle the essentials of urban analysis, like `loading` data, `filling gaps`, `filtering`, `enriching`, and `visualising`. They’re the foundation of what makes `UrbanMapper` unique and are designed to work seamlessly within its framework.
      - **Mixins**, by contrast, are enhancements powered by external libraries and APIs. They bring in outside tools—like `Skrub` for interactive visuals, `JupyterGIS` for collaborative mapping, or `Auctus` for dataset searches—to extend `UrbanMapper`’s capabilities. While modules are the heart of the system, mixins are optional add-ons that tap into existing solutions to tackle specific urban challenges.


!!! important "How To Understand How To Use The `External Libraries` Supported?"
    The user guides focusses primarily the `UrbanMapper` modules. For the external libraries,
    please refer to the `examples` folder in the `UrbanMapper` repository. They are shown in actions.

    [Open Examples :fontawesome-brands-python:](https://github.com/VIDA-NYU/UrbanMapper/tree/main/examples){ .md-button } [Open Examples Explainations :fontawesome-solid-compass:](../getting-started/examples.md){ .md-button }

## 🚀 Ready to Read Through Each of The Modules ?

Dive into these sections to master `UrbanMapper`’s full potential:

- **[1 - Loaders](loaders.md)**: Get your geospatial data loaded and primed for action.
- **[2 -Urban Layers](urban-layers.md)**: Shape the spatial backbone of your analysis—streets, neighborhoods, and more.
- **[3 -Imputers](imputers.md)**: Tackle missing data like a pro, keeping your analysis solid.
- **[4 - Filters](filters.md)**: Zero in on the details—by bounding box.
- **[5 - Enrichers](enrichers.md)**: Layer on insights, like counting trees per neighborhood.
- **[6 - Visualisers](visualisers.md)**: Craft stunning maps and charts that tell the story.
- **[7 - Pipelines](pipelines.md)**: Build reproducible, shareable workflows from start to finish.
- **[8 - Pipeline Generators](pipeline-generators.md)**: Let LLMs whip up pipelines from your ideas.
