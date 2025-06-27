# Visualisers

!!! tip "What is the visualiser module?"
    The `visualiser` module is responsible to deliver visualiser's primitives such as matplotlib or folium,
    following a `UrbanMapper`'s analysis.

    Meanwhile, we recommend to look through the [`Example`'s Visualiser](../copy_of_examples/1-Per-Module/6-visualiser/) for a more hands-on introduction about
    the Visualiser module and its usage.
 

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