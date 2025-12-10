# API Reference

## Core Modules

<div class="grid cards core" markdown>

-   :material-database:{ .lg .middle } __Loaders__

    ---

    Unified interfaces to load geospatial datasets (CSV, Parquet, Shapefile, DataFrame, HuggingFace) with latitude/longitude or WKT geometry.

    [:octicons-book-24: Docs](./loaders.md){ .md-button .md-button--primary }

-   :simple-openstreetmap:{ .lg .middle } __Urban Layers__

    ---

    Spatial canvases (streets, intersections, OSM features, neighborhoods, cities, states, countries, custom layers) for projecting datasets.

    [:octicons-book-24: Docs](./urban_layers.md){ .md-button .md-button--primary }

-   :material-filter-outline:{ .lg .middle } __Filters__

    ---

    Filter geospatial data by bounding boxes and other criteria using lat/long columns or WKT geometries.

    [:octicons-book-24: Docs](./filters.md){ .md-button .md-button--primary }

-   :material-auto-fix:{ .lg .middle } __Imputers__

    ---

    Handle missing geospatial information (coordinates, geometries) with simple and address-based imputers.

    [:octicons-book-24: Docs](./imputers.md){ .md-button .md-button--primary }

-   :material-function-variant:{ .lg .middle } __Enrichers__

    ---

    Turn urban layers into meaningful statistics (counts per intersection, averages per neighborhood) with pluggable aggregators.

    [:octicons-book-24: Docs](./enrichers.md){ .md-button .md-button--primary }

-   :material-map-search-outline:{ .lg .middle } __Visualisers__

    ---

    Static and interactive visualisation primitives for rendering your results.

    [:octicons-book-24: Docs](./visualisers.md){ .md-button .md-button--primary }

-   :simple-jfrogpipelines:{ .lg .middle } __Pipeline__

    ---

    Compose loaders, layers, filters, imputers, enrichers, and visualisers into a single executable pipeline.

    [:octicons-book-24: Docs](./pipelines.md){ .md-button .md-button--primary }

</div>

---

## Optional Modules

<div class="grid cards optional" markdown>

-   :material-robot-outline:{ .lg .middle } __Pipeline Generators__

    ---

    Generate UrbanMapper pipelines from natural language with LLMs.

    [:octicons-book-24: Docs](./pipeline_generators.md){ .md-button }

-   :material-database-search:{ .lg .middle } __Auctus Mixin__

    ---

    Query the Auctus Dataset Search API inside the UrbanMapper workflow.

    [:octicons-book-24: Docs](./auctus.md){ .md-button }

-   :material-table:{ .lg .middle } __Interactive Table VIS__

    ---

    Explore datasets interactively in notebooks with richer tables and attribute statistics.

    [:octicons-book-24: Docs](./interactive_table_vis.md){ .md-button }

-   :material-earth:{ .lg .middle } __JupyterGIS Mixin__

    ---

    Collaboratively explore pipelines and geodata via Jupyter GIS.

    [:octicons-book-24: Docs](./jupyter_gis.md){ .md-button }

</div>