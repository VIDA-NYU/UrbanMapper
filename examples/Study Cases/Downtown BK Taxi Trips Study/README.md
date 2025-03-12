<div align="center">
   <h1>Taxi Trip Analysis in Downtown Brooklyn</h1>
   <h3>Mapping Pickups and Dropoffs to Street Segments with OSMNxMapping</h3>
    <p><i>for urban mobility insights</i></p>
   <p>
      <img src="https://img.shields.io/static/v1?label=Python&message=3.9%2B&color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
      <img src="https://img.shields.io/badge/OSMNxMapping-4CAF50?style=for-the-badge&logo=openstreetmap&logoColor=white" alt="OSMNxMapping">
      <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter">
      <img src="https://img.shields.io/badge/Status-In%20Progress-blue?style=for-the-badge" alt="In Progress">
   </p>
   <p>Map taxi pickup and dropoff data to Downtown Brooklyn's street segments, uncover mobility patterns, and enhance urban planning with data-driven insights.</p>
</div>

---

<div style="text-align: center;">
  <img src="./resources/taxi_analysis_cover.png" alt="Taxi Analysis Cover">
</div>

> [!IMPORTANT]
> 1) Explore the `/Study Cases` folder for hands-on Jupyter Notebook tutorials 🎉  
> 2) This study is actively evolving—expect updates as `OSMNxMapping` develops!

## 🚕 Taxi Trip Analysis –– In a Nutshell

This study maps **taxi pickups and dropoffs** in **Downtown Brooklyn** to **street segments and intersections** using `OSMNxMapping`. By integrating taxi trip data with OpenStreetMap street networks, we reveal spatial patterns of urban mobility and provide insights for smarter urban planning.

<details>
<summary><strong> 👀 What’s Inside? Click here ⬅️</strong></summary>

- **[1] Downtown_BK_Taxi_Trips_OSMNX_StepByStep.ipynb**  
  A step-by-step tutorial covering:
  - Loading taxi trip data from CSV.
  - Querying the Downtown Brooklyn street network.
  - Preprocessing data (imputing missing coordinates, filtering to a bounding box).
  - Mapping pickups and dropoffs to street nodes.
  - Enriching the network with pickup and dropoff counts.
  - Visualising results interactively (streets and intersections) and statically (intersections).

- **[2] Downtown_BK_Taxi_Trips_OSMNX_Pipeline.ipynb**  
  A streamlined `UrbanPipeline` automating:
  - Data loading and network creation.
  - Imputation and filtering.
  - Mapping and enriching with pickup/dropoff counts.
  - Interactive visualisation of streets and intersections—all in a concise workflow.

- **[3] Downtown_BK_Taxi_Trips_OSMNX_Advanced_Pipeline.ipynb**  
  An advanced `UrbanPipeline` extending the basic pipeline with:
  - Additional enrichment for average fare amount per street segment/intersection.
  - Interactive visualisation of pickup counts, dropoff counts, and average fares.

</details>

---

## 🥐 Getting Started

1. **Install OSMNxMapping**: Follow the [installation guide](https://github.com/VIDA-NYU/OSMNxMapping#installation).
2. **Prepare Data**: Ensure your taxi trip data (e.g., `taxi_trips.csv`) includes columns:
   - `pickup_longitude`, `pickup_latitude`
   - `dropoff_longitude`, `dropoff_latitude`
   - (Optional) `fare_amount` for advanced metrics.
3. **Run Notebooks**: Open the `/Study Cases` folder in Jupyter and start exploring!

## 🛣️ Why It Matters

Analysing taxi activity enables cities to:
- Pinpoint high-demand streets and intersections.
- Optimise traffic flow and ride-sharing efficiency.
- Inform infrastructure planning with mobility data.

Your insights could drive impactful urban solutions!

---

## 🗺️ Roadmap / Future Work

- **Temporal Analysis**: Investigate pickup/dropoff trends by time of day or week.
- **Extended Metrics**: Add trip distance, passenger counts, or congestion indicators.
- **Scalability**: Adapt the pipeline for larger regions or datasets.

Have suggestions? Fork the repo or share ideas in [issues](https://github.com/VIDA-NYU/OSMNxMapping/issues)!

---

## Data Sources

- **[Yellow NYC Taxis 2015](https://arc.net/l/quote/pwljlsqk)**: Sample taxi trip data for NYC. We simply used a million sample from the original data for the sake of the example.
---

## Licence

Shared under the [MIT Licence](https://github.com/VIDA-NYU/OSMNxMapping/blob/main/LICENCE).