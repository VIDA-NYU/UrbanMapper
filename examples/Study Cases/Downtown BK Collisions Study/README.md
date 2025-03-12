<div align="center">
   <h1>Motor Vehicle Collision Analysis in Downtown Brooklyn</h1>
   <h3>Mapping Collisions to Street Networks with OSMNxMapping</h3>
    <p><i>for urban safety insights</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Python&message=3.9%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
      <img src="https://img.shields.io/badge/OSMNxMapping-4CAF50?style=for-the-badge&logo=openstreetmap&logoColor=white" alt="OSMNxMapping">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/badge/Status-In%20Progress-blue?style=for-the-badge" alt="In Progress">
   </p>
   <p>Map collision data to Downtown Brooklyn's streets, uncover patterns, and improve urban safety with data-driven insights.</p>
</div>

---

<div style="text-align: center;">
  <img src="./resources/collision_analysis_cover.png" alt="Collision Analysis Cover">
</div>

> [!IMPORTANT]
> 1) Check out the `/Study Cases` folder for hands-on Jupyter Notebook tutorials 🎉  
> 2) This study is under active development—expect updates, tweaks, and maybe refactoring since `UrbanMapper` is under dev. and successor of this project!

## 🚗 Collision Analysis –– In a Nutshell

This study maps **Downtown Brooklyn motor vehicle collisions** to **street intersections** using `OSMNxMapping`.  
To improve urban safety research, we link collision data to OpenStreetMap road networks to reveal hotspots and patterns.

<details>
<summary><strong> 👀 What’s Inside? Click here ⬅️</strong></summary>

- **[1] Downtown_BK_Collisions_OSMNX_StepByStep.ipynb**  
  A detailed, procedural implementation leveraging OSMNxMapping to ingest NYC DOT collision data from CSV, construct a drivable street network for Downtown Brooklyn via OSM queries, preprocess geospatial data (imputation via SimpleGeoImputer, spatial filtering with BoundingBoxFilter), map collisions to nearest intersections using node-based nearest-neighbor assignment, enrich the network with collision counts per node, and render an interactive Folium visualisation—ideal for dissecting each computational stage.

- **[2] Downtown_BK_Collisions_OSMNX_Pipeline.ipynb**  
  A streamlined UrbanPipeline automating the collision mapping process described in [1] in ~10 lines—query network, load, map, enrich, visualise—all in one go.

- **[3] Downtown_BK_Collisions_OSMNX_Advanced_Pipeline.ipynb**  
  An advanced pipeline compared to [2] exploring collision severity (more than one enriching process all-in-one). I.e. injuries, and fatalities.

Each notebook is modular and primed for customization—adapt them to your geospatial datasets with ease!

</details>
---

## 🥐 Getting Started

1. **Set Up OSMNxMapping**: Follow the [installation guide](https://github.com/VIDA-NYU/OSMNxMapping#installation) from the main repo.
2. **Dive into Notebooks**: Open the `/Study Cases` folder in Jupyter to start exploring collision data.
3. **Make It Yours**: Adapt the pipelines to analyse collisions (or other data) in your city/neighborhood of choice!

## 🛣️ Why It Matters

Collisions are a big deal in cities. This study:

- Spots high-risk intersections with precision.  
- Visualises trends in a snap with interactive maps.  
- Fuels smarter safety solutions for urban planners and communities.  

Your analysis could help save lives—one street at a time!

---

## 🗺️ Roadmap / Future Work

- **Time Trends**: Map how collisions change by hour, day, or season. Further will be available when `UrbanMapper` sees the light of day.
- **Cause Analysis**: Link crashes to factors like road design or weather, maybe via `LLM` && `Causality` now that you have the "enriched" data 👀.

Got ideas? Fork the repo, tweak the code, or drop suggestions in [issues](https://github.com/VIDA-NYU/OSMNxMapping/issues)!

---

## Data Sources

- **[NYC DOT Motor Vehicle Collisions](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)**  

---

## Licence

This study is shared under the [MIT Licence](https://github.com/VIDA-NYU/OSMNxMapping/blob/main/LICENCE).
