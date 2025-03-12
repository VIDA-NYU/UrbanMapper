#!/usr/bin/env python
# coding: utf-8

# In[27]:


import osmnx_mapping as oxm
from osmnx_mapping.pipeline import UrbanPipeline
from osmnx_mapping.modules.loader import CSVLoader
from osmnx_mapping.modules.preprocessing import CreatePreprocessor
from osmnx_mapping.modules.enricher import CreateEnricher
from osmnx_mapping.modules.visualiser import InteractiveVisualiser
from osmnx_mapping.modules.network import CreateNetwork


# In[28]:


collisions_study = oxm.OSMNxMapping()


# In[29]:


pipeline = UrbanPipeline(
    [
        # Load collision data from CSV file
        (
            "load",
            CSVLoader(
                file_path="./../../data/ACCIDENTS/NYC/CSV/NYC_Motor_Vehicle_Collisions_Mar_12_2025.csv"
            ),
        ),
        # Build Downtown Brooklyn street network and prepare mapper to map data to nearest intersections with threshold =
        (
            "network",
            CreateNetwork()
            .with_place("Downtown, Brooklyn, New York, USA", network_type="drive")
            .with_mapping(
                mapping_type="node",
                output_column="nearest_intersection",
                longitude_column_name="LONGITUDE",
                latitude_column_name="LATITUDE",
            )
            .build(),
        ),
        # Drop rows missing latitude or longitude
        (
            "impute",
            CreatePreprocessor()
            .with_imputer(
                imputer_type="SimpleGeoImputer",
            )
            .build(),
        ),
        # Keep only data within the network's bounding box
        (
            "filter",
            CreatePreprocessor().with_filter(filter_type="BoundingBoxFilter").build(),
        ),
        # Count collisions per intersection
        (
            "enrich",
            CreateEnricher()
            .with_data(group_by="nearest_intersection")
            .count_by(target="nodes", output_column="collision_count")
            .build(),
        ),
        # Enable interactive result visualization
        ("viz", InteractiveVisualiser()),
    ]
)


# In[30]:


data, graph, nodes, edges = pipeline.compose_transform(
    latitude_column_name="LATITUDE", longitude_column_name="LONGITUDE"
)


# In[34]:


# Visualise the enriched network on intersections (nodes)
viz = pipeline.visualise(
    result_columns="collision_count",
    target="nodes",
    colormap="Reds",
    tile_provider="Cartodb dark_matter",
)
viz


# In[ ]:
