<div align="center">
   <h1>UrbanMapper</h1>
   <h3>Enrich Urban Layers Given Urban Datasets</h3>
   <p><i>with ease-of-use API and Sklearn-alike Shareable & Reproducible Urban Pipeline</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Beartype&message=compliant&color=4CAF50&style=for-the-badge&logo=https://avatars.githubusercontent.com/u/63089855?s=48&v=4&logoColor=white" alt="Beartype compliant">
      <img src="https://img.shields.io/static/v1?label=UV&message=compliant&color=2196F3&style=for-the-badge&logo=UV&logoColor=white" alt="UV compliant">
      <img src="https://img.shields.io/static/v1?label=RUFF&message=compliant&color=9C27B0&style=for-the-badge&logo=RUFF&logoColor=white" alt="RUFF compliant">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
      <img src="https://img.shields.io/github/actions/workflow/status/VIDA-NYU/UrbanMapper/compile.yaml?style=for-the-badge&label=Compilation&logo=githubactions&logoColor=white" alt="Compilation Status">
   </p>
</div>



![UrbanMapper Cover](./public/resources/urban_mapper_cover.png)


___

## `UrbanMapper`, In a Nutshell

`UrbanMapper` lets you link your data to spatial features—matching, for example, traffic events to streets—to enrich
each location with meaningful, location-based information. Formally, it defines a spatial enrichment
function $f(X, Y) = X \bowtie Y$, where $X$ represents urban layers (e.g., `Streets`, `Sidewalks`, `Intersections` and
more)
and $Y$ is a user-provided dataset (e.g., `traffic events`, `sensor data`). The operator $\bowtie$ performs a spatial
join, enriching each feature in $X$ with relevant attributes from $Y$.

In short, `UrbanMapper` is a Python toolkit that enriches typically plain urban layers with datasets in a reproducible,
shareable, and easily updatable way using minimal code. For example, given `traffic accident` data and a `streets` layer
from [OpenStreetMap](https://www.openstreetmap.org), you can compute accidents per street with
a [Scikit-Learn](https://scikit-learn.org/stable/)–style pipeline called the `Urban Pipeline`—in under 15 lines of code.
As your data evolves or team members want new analyses, you can share and update the `Urban Pipeline` like a trained
model, enabling others to run or extend the same workflow without rewriting code.

There are more to `UrbanMapper`, explore!

See a trailer-style video below to get a quick overview of `UrbanMapper` and its features:

<div align="center">
<iframe width="660" height="415" src="https://www.youtube-nocookie.com/embed/QUmfvda_z2U?si=nXKwC4_LA1C99ZR_&amp;controls=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

## `Urban Layers` Currently Supported

`UrbanMapper` currently supports the following `urban layers`:

- [x] **Streets Roads** – Loads street road networks from [OpenStreetMap](https://www.openstreetmap.org) (OSM) using [OSMNx](https://osmnx.readthedocs.io/en/stable/).
- [x] **Streets Intersections** – Loads street intersections from OSM using [OSMNx](https://osmnx.readthedocs.io/en/stable/).
- [x] **Sidewalks** – Loads sidewalks via [Tile2Net](https://github.com/VIDA-NYU/tile2net) using Deep Learning for automated mapping of pedestrian infrastructure from aerial imagery.
- [x] **Cross Walks** – Loads crosswalks via [Tile2Net](https://github.com/VIDA-NYU/tile2net) using Deep Learning for automated mapping of pedestrian infrastructure from aerial imagery.
- [x] **Cities' Features** – Loads OSM city features such as buildings, parks, bike lanes, etc., via [OSMNx](https://osmnx.readthedocs.io/en/stable/) API.
- [x] **Region Neighborhoods** – Loads neighborhood boundaries from OSM using [OSMNx](https://osmnx.readthedocs.io/en/stable/) Features module.
- [x] **Region Cities** – Loads city boundaries from OSM using [OSMNx](https://osmnx.readthedocs.io/en/stable/) Features module.
- [x] **Region States** – Loads state boundaries from OSM using [OSMNx](https://osmnx.readthedocs.io/en/stable/) Features module.
- [x] **Region Countries** – Loads country boundaries from OSM using [OSMNx](https://osmnx.readthedocs.io/en/stable/) Features module.
- [ ] **Subway/Tube** – Planned support for loading subway/tube networks.

More `urban layers` will be added in the future.
Suggestions? Open an issue or pull request on our [GitHub repository](https://github.com/VIDA-NYU/UrbanMapper/issues).

___

## `UrbanMapper` – Use Cases by `Urban Layer`

`UrbanMapper` is a flexible tool for addressing a wide range of urban analysis challenges. This non-exhaustive list of
practical use cases showcases its capabilities in `transportation`, `safety`, `environment`, `demographics`, and
`urban planning` scenarios among others based on each `urban layer` supported.

=== "🛣️ Streets Roads"

    - **Analyse traffic congestion patterns**  
      Load traffic sensor data, filter by peak hours, and enrich with road type information to visualise congestion on `streets roads`.

    - **Optimise traffic signal timings**  
      Use real-time traffic data to dynamically adjust signal timings on `streets roads`, reducing congestion and improving flow.

    - **Map air pollution levels**  
      Overlay air quality sensor data onto `streets roads` to identify high-pollution zones and target emissions reduction efforts.

=== "🚦Streets Intersections"

    - **Map taxi pickup/dropoff patterns**  
      Analyse taxi activity to identify high-traffic `street intersections` for optimising ride-sharing hubs or traffic flow.

    - **Analyse collision hotspots**  
      Pinpoint `street intersections` with frequent accidents to implement safety measures like better signage or signal adjustments.

    - **Evaluate vehicle wait times**  
      Study wait times at `street intersections` to optimise traffic management and reduce delays.

=== "🚶🚶‍♀️Sidewalks"

    - **Evaluate pedestrian safety**  
      Map accident or complaint data to `sidewalks` to identify hazardous areas needing maintenance or infrastructure upgrades.

    - **Study the effect of sidewalk quality on pedestrian traffic**  
      Correlate pedestrian volume with `sidewalk` conditions (e.g., width, surface quality) to prioritise improvements.

    - **Assess walkability in urban areas**  
      Analyse `sidewalk` networks and proximity to amenities to calculate walkability scores for different zones.

=== "🚷Cross Walks"

    - **Analyse collision hotspots around `cross walks`**  
      Map crash data to `cross walks` to identify accident-prone locations and improve pedestrian safety measures.

    - **Optimise pedestrian signal timings**  
      Use pedestrian traffic data at `cross walks` to adjust signal timings for better flow and safety.

    - **Evaluate crosswalk accessibility**  
      Assess the distribution and condition of `cross walks` to ensure equitable access for all pedestrians.

=== "🌉 Cities' Features"

    - **Assess the impact of `bike lanes` on traffic flow**  
      Study how `bike lanes` affect vehicle speeds and accident rates on adjacent roads.

    - **Plan urban green spaces**  
      Analyse the distribution of `parks` to identify areas lacking accessible green spaces for future development.

    - **Analyse noise pollution near `building footprints`**  
      Overlay noise data onto `building footprints` to identify residential areas needing soundproofing or noise barriers.

=== "🌎Regions Layers"

    **🏘️ Neighborhoods**:

    - **Evaluate public transportation coverage**  
      Map transit stops to neighborhoods to identify underserved areas and plan service improvements.
    - **Enrich data with demographic information**  
      Overlay census data on neighborhoods to reveal population trends, income levels, or age distributions for targeted urban planning.
    - **Analyse tourist greenery**  
      Map remarkable trees or green spaces to neighborhoods to assess their impact on tourism and urban greening.
    
    **🌆 Cities**:

    - **Compare urban density**  
      Use building footprints or population data to assess and compare density across cities for regional planning.
    - **Analyse economic activity**  
      Map business locations or employment data to cities to identify economic hubs and growth opportunities.
    - **Study transportation connectivity**  
      Analyse road or rail networks across cities to optimise infrastructure and reduce congestion.
    
    **🌍 States**:

    - **Study environmental impacts**  
      Overlay climate or pollution data across states to compare conditions and plan statewide initiatives.
    - **Analyse transportation networks**  
      Map highway or rail networks across states to optimise connectivity and prioritise infrastructure investments.
    - **Evaluate policy effectiveness**  
      Compare demographic or economic data across states to assess the impact of state-level policies.
    
    **🌐 Countries**:

    - **Analyse global urban trends**  
      Compare urbanization rates or infrastructure development across countries for international studies.
    - **Map international trade routes**  
      Overlay trade data onto countries to visualise global economic connections and dependencies.
    - **Study climate resilience**  
      Analyse temperature changes or natural disaster data across countries to assess vulnerability and plan mitigation strategies.

---

# Where To Get Started ?

- [Installation](getting-started/installation.md): How to install `UrbanMapper`
- [Getting Started Step By Step](getting-started/quick-start_step_by_step.md): Create your first `UrbanMapper`'s
  analysis
  step-by-step.
- [Getting Started W/ Pipeline](getting-started/quick-start_pipeline.md): Create your first `UrbanMapper`'s analysis w/
  pipeline.
- [Urban Mapper's Examples](./EXAMPLES.md): Explore the `examples/` interactively via Jupyter notebooks.
- [API Reference](api/loaders.md): Complete API documentation
