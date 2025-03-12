#!/usr/bin/env python
# coding: utf-8

# In[28]:


# Import necessary modules
import osmnx_mapping as oxm
from osmnx_mapping.modules.preprocessing import CreatePreprocessor
from osmnx_mapping.modules.enricher import CreateEnricher
from osmnx_mapping.modules.visualiser import InteractiveVisualiser, StaticVisualiser


# In[17]:


# Initialise an OSMNxMapping instance
collisions_study = oxm.OSMNxMapping()


# In[18]:


# Step 1: Query the street network for Downtown Brooklyn
graph, nodes, edges = collisions_study.road_networks.network_from_place(
    "Downtown, Brooklyn, New York, USA", network_type="drive", render=True
)


# In[19]:


# Step 2: Load collision data from CSV file
data = collisions_study.loader.load_from_file(
    file_path="./../../data/ACCIDENTS/NYC/CSV/NYC_Motor_Vehicle_Collisions_Mar_12_2025.csv",
    latitude_column="LATITUDE",
    longitude_column="LONGITUDE",
)
# This loads the CSV into a GeoDataFrame, setting the geometry based on LATITUDE and LONGITUDE columns.


# Feel free to use the interactive table viz as follows (click on column name latitude and or longitude):
collisions_study.table_vis.interactive_display(data)


# In[20]:


# Step 3: Impute missing values by dropping rows with missing latitude or longitude as above we detected missing values
# SimpleGeoImputer removes rows where LATITUDE or LONGITUDE is missing, ensuring valid geospatial data. More primitives exists! This one is just basic.
imputer = (
    CreatePreprocessor()
    .with_imputer(
        imputer_type="SimpleGeoImputer",
        latitude_column_name="LATITUDE",
        longitude_column_name="LONGITUDE",
    )
    .build()
)

data = imputer.transform(data)


# Feel free to use the interactive table viz as follows:
collisions_study.table_vis.interactive_display(data)


# In[21]:


# Step 4: Filter data to keep only points within the network's bounding box
# This retains only the data points that fall within the spatial extent of the network's nodes.
filterer = (
    CreatePreprocessor()
    .with_filter(filter_type="BoundingBoxFilter", nodes=nodes)
    .build()
)
data = filterer.transform(data)


# Feel free to use the interactive table viz as follows (look at the number of rows):
collisions_study.table_vis.interactive_display(data)


# In[22]:


# Step 5: Map collision data to the nearest intersections (nodes)
# This adds a 'nearest_intersection' column to the data, identifying the closest node for each collision.

data = collisions_study.road_networks.map_nearest_street(
    data=data,
    longitude_column="LONGITUDE",
    latitude_column="LATITUDE",
    output_column="nearest_intersection",
)


# Feel free to use the interactive table viz as follows (look at the new column by the end):
collisions_study.table_vis.interactive_display(data)


# In[25]:


# Step 6: Enrich the network by counting collisions per node (intersections)
# This counts the number of collisions per node and attaches the 'collision_count' to the enriched nodes.

enricher = (
    CreateEnricher()
    .with_data(group_by="nearest_intersection")
    .count_by(target="nodes", output_column="collision_count")
    .build()
)

enriched_data, enriched_graph, enriched_nodes, enriched_edges = enricher.enrich(
    data, graph=graph, nodes=nodes, edges=edges
)


# In[27]:


# Step 7: Visualise the enriched network interactively
# This creates an interactive map showing collision counts at nodes, styled with a red colormap on a dark Folium basemap.

visualiser = InteractiveVisualiser()

viz = visualiser.render(
    graph=enriched_graph,
    nodes=enriched_nodes,
    edges=enriched_edges,
    result_columns="collision_count",
    target="nodes",
    colormap="Reds",
    tile_provider="Cartodb dark_matter",
)
viz


# In[29]:


# Step 8: Visualise the enriched network Statically
# This creates a static mat plot lib viz showing collision counts at nodes, styled with a red colormap.

visualiser = StaticVisualiser()

viz = visualiser.render(
    graph=enriched_graph,
    nodes=enriched_nodes,
    edges=enriched_edges,
    result_columns="collision_count",
    target="nodes",
    colormap="Reds",
    tile_provider="Cartodb dark_matter",
)
viz


# In[ ]:
