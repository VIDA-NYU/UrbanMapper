#!/usr/bin/env python
# coding: utf-8

# ## Step 1: Import Modules

# In[ ]:


import osmnx_mapping as oxm
from osmnx_mapping.modules.preprocessing import CreatePreprocessor
from osmnx_mapping.modules.enricher import CreateEnricher
from osmnx_mapping.modules.visualiser import InteractiveVisualiser, StaticVisualiser
from IPython.display import display


# ## Step 2: Initialise OSMNxMapping

# In[ ]:


taxi_study = oxm.OSMNxMapping()


# ## Step 3: Query the Street Network

# In[ ]:


graph, nodes, edges = taxi_study.road_networks.network_from_place(
    "Downtown, Brooklyn, New York, USA", network_type="drive", render=True
)


# ## Step 4: Load Taxi Trip Data

# In[ ]:


data = taxi_study.loader.load_from_file(
    file_path="./../../../data/TAXIS/csv/taxisvis1M.csv",
    latitude_column="pickup_latitude",  # Innapropriate will change in Urban Mapper
    longitude_column="pickup_longitude",  # Innapropriate will change in Urban Mapper
)
taxi_study.table_vis.interactive_display(data)


# ## Step 5: Impute Missing Coordinates

# In[ ]:


# ( Not necessary if no missing values are presented below )

# Impute pickups
imputer_pickup = (
    CreatePreprocessor()
    .with_imputer(
        imputer_type="SimpleGeoImputer",
        latitude_column_name="pickup_latitude",
        longitude_column_name="pickup_longitude",
    )
    .build()
)
data = imputer_pickup.transform(data)

# Impute dropoffs
imputer_dropoff = (
    CreatePreprocessor()
    .with_imputer(
        imputer_type="SimpleGeoImputer",
        latitude_column_name="dropoff_latitude",
        longitude_column_name="dropoff_longitude",
    )
    .build()
)
data = imputer_dropoff.transform(data)

taxi_study.table_vis.interactive_display(data)


# ## Step 6: Filter to Bounding Box

# In[ ]:


filterer = (
    CreatePreprocessor()
    .with_filter(filter_type="BoundingBoxFilter", nodes=nodes)
    .build()
)

data = filterer.transform(data)

taxi_study.table_vis.interactive_display(data)


# ## Step 7: Map to Street Segments

# In[ ]:


# Map pickups
data = taxi_study.road_networks.map_nearest_street(  # Name is innapropriate, things will change in Urban Mapper
    data=data,
    longitude_column="pickup_longitude",
    latitude_column="pickup_latitude",
    output_column="pickup_node",
)

# Map dropoffs
data = taxi_study.road_networks.map_nearest_street(  # Name is innapropriate, things will change in Urban Mapper
    data=data,
    longitude_column="dropoff_longitude",
    latitude_column="dropoff_latitude",
    output_column="dropoff_node",
)

taxi_study.table_vis.interactive_display(data)


# ## Step 8: Enrich the Network

# In[ ]:


# Enrich with pickup counts
enricher_pickup = (
    CreateEnricher()
    .with_data(group_by="pickup_node")
    .count_by(target="both", output_column="pickup_count")
    .build()
)
enriched_data, enriched_graph, enriched_nodes, enriched_edges = enricher_pickup.enrich(
    data, graph=graph, nodes=nodes, edges=edges
)

# Enrich with dropoff counts
enricher_dropoff = (
    CreateEnricher()
    .with_data(group_by="dropoff_node")
    .count_by(target="both", output_column="dropoff_count")
    .build()
)

enriched_data, enriched_graph, enriched_nodes, enriched_edges = enricher_dropoff.enrich(
    enriched_data, graph=enriched_graph, nodes=enriched_nodes, edges=enriched_edges
)


# ## Step 9: Visualise Interactively (streets)

# In[ ]:


visualiser = InteractiveVisualiser()
viz = visualiser.render(
    graph=enriched_graph,
    nodes=enriched_nodes,
    edges=enriched_edges,
    result_columns=["pickup_count", "dropoff_count"],
    target="edges",
    colormap="Blues",
    tile_provider="Cartodb dark_matter",
)
viz


# ## Step 10: Visualise Interactively (intersections)

# In[ ]:


visualiser = InteractiveVisualiser()
viz = visualiser.render(
    graph=enriched_graph,
    nodes=enriched_nodes,
    edges=enriched_edges,
    result_columns=["pickup_count", "dropoff_count"],
    target="nodes",
    colormap="Blues",
    tile_provider="Cartodb dark_matter",
)
viz


# ## Step 11: Visualise Static (intersections)

# In[ ]:

visualiser = StaticVisualiser()

print("######## Pickup:")

pickup = visualiser.render(
    graph=enriched_graph,
    nodes=enriched_nodes,
    edges=enriched_edges,
    result_columns="pickup_count",
    target="nodes",
    colormap="Blues",
    tile_provider="Cartodb dark_matter",
)

display(pickup)

print("######## Dropoff:")


dropoff = visualiser.render(
    graph=enriched_graph,
    nodes=enriched_nodes,
    edges=enriched_edges,
    result_columns="dropoff_count",
    target="nodes",
    colormap="Blues",
    tile_provider="Cartodb dark_matter",
)

display(dropoff)


# In[ ]:
