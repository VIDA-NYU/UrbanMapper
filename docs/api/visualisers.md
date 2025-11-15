# Visualisers

!!! tip "What is the visualiser module?"
    The `visualiser` module is responsible to deliver visualiser's primitives such as matplotlib, folium and lonboard.
    following a `UrbanMapper`'s analysis.

    Meanwhile, we recommend to look through the [`Example`'s Visualiser](../copy_of_examples/1-Per-Module/6-visualiser/)
    for a more hands-on introduction about the Visualiser module and its usage.

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change,
    and some parts might be incomplete or inaccurate.

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

!!! note "Visualiser identifiers"
        
    | Visualiser            | When to pick it                                                                 |
    |-----------------------|----------------------------------------------------------------------------------|
    | `lonboard_classic`    | Recommended default for interactive exploration across polygons, lines, points — High quality map viz. |
    | `lonboard_heatmap`    | Dense point clouds where a smoothed intensity surface is easier to interpret — Heatmap viz analysis |
    | `geopandas_interactive` | Quick Folium maps with dropdown selection but lighter dependencies — Rather lightweight map viz.            |
    | `geopandas_static`    | Matplotlib exports or notebook screenshots — useful for papers.                 |


## API reference

### ::: urban_mapper.modules.visualiser.VisualiserBase
    options:
        heading: "VisualiserBase"
        members:
            - _render
            - render
            - preview

### ::: urban_mapper.modules.visualiser.StaticVisualiser
    options:
        heading: "StaticVisualiser"
        members:
            - _render
            - preview

### ::: urban_mapper.modules.visualiser.InteractiveVisualiser
    options:
        heading: "InteractiveVisualiser"
        members:
            - _render
            - preview

### ::: urban_mapper.modules.visualiser.LonboardClassicVisualiser
    options:
        heading: "LonboardClassicVisualiser"
        members:
            - _render
            - preview

### ::: urban_mapper.modules.visualiser.LonboardHeatmapVisualiser
    options:
        heading: "LonboardHeatmapVisualiser"
        members:
            - _render
            - preview

??? example "Lonboard medium-to-advanced styling"
    This example shows how to combine multiple style hooks, including a
    `colormap`, layer kwargs, and Map configuration for Lonboard visualisers.

    ```python
    from lonboard.basemap import CartoStyle, MaplibreBasemap
    from lonboard.controls import NavigationControl, ScaleControl

    visualiser = (
        mapper.visual
        .with_type("lonboard_classic")
        .with_style({
            "colormap": {
                "target": "polygon",
                "column": "avg_fare", # This assume avg_fare is a column in the polygon GeoDataFrame and the `only one of interest`.
                "palette": "viridis",
                "vmin": 5,
                "vmax": 65,
                "alpha": 0.9,
                "nan_color": [128, 128, 128, 100],
            },
            "map_kwargs": {
                "basemap": MaplibreBasemap(
                    mode="interleaved",
                    style=CartoStyle.DarkMatterNoLabels,
                ),
                "show_tooltip": True,
            },
            "controls": [
                NavigationControl(position="top-right"),
                ScaleControl(position="bottom-left", unit="imperial"),
            ],
        })
        .build()
    )
    ```

    The colormap paints the polygons by `avg_fare`, while point features inherit
    a custom fill colour and radius. Map controls are added directly through the
    supported `controls` style entry, and everything merges into the final
    `lonboard.Map` configuration.

    The above is strictly for advanced usages, no need for all that for basic usage.


## ::: urban_mapper.modules.visualiser.VisualiserFactory
    options:
        heading: "VisualiserFactory"
        members:
            - with_type 
            - with_style
            - show
            - render
            - build
            - preview
            - with_preview
