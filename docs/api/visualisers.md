# Visualisers

!!! tip "What is the visualiser module?"
    The `visualiser` module is responsible to deliver visualiser's primitives such as matplotlib or folium,
    following a `UrbanMapper`'s analysis.

    We highly recommend to look through the `User Guide`'s Visualiser section for a more in-depth introduction about
    the visualiser module and its usage prior to explore its API.

    [See The User Guide :fontawesome-solid-signs-post:](../user-guide/modules/6-visualisers.md){ .md-button } 

!!! warning "Documentation Under Alpha Construction"
    **This documentation is in its early stages and still being developed.** The API may therefore change, 
    and some parts might be incomplete or inaccurate.  

    **Use at your own risk**, and please report anything that seems `incorrect` / `outdated` you find.

    [Open An Issue! :fontawesome-brands-square-github:](https://github.com/VIDA-NYU/UrbanMapper/issues){ .md-button }

## ::: urban_mapper.modules.visualiser.VisualiserBase
    options:
        heading: "VisualiserBase"
        members:
            - _render 
            - render 
            - preview

## ::: urban_mapper.modules.visualiser.StaticVisualiser
    options:
        heading: "StaticVisualiser"
        members:
            - _render 
            - preview

## ::: urban_mapper.modules.visualiser.InteractiveVisualiser
    options:
        heading: "StaticVisualiser"
        members:
            - _render 
            - preview

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