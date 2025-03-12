#!/usr/bin/env python
# coding: utf-8

# In[1]:


import osmnx_mapping as oxm
from osmnx_mapping.pipeline import UrbanPipeline
from osmnx_mapping.modules.loader import CSVLoader
from osmnx_mapping.modules.preprocessing import CreatePreprocessor
from osmnx_mapping.modules.enricher import CreateEnricher
from osmnx_mapping.modules.visualiser import InteractiveVisualiser
from osmnx_mapping.modules.network import CreateNetwork


# In[2]:


collisions_study = oxm.OSMNxMapping()


# In[3]:


pipeline = UrbanPipeline(
    [
        # Load collision data from CSV file
        (
            "load",
            CSVLoader(
                file_path="./../../data/ACCIDENTS/NYC/CSV/NYC_Motor_Vehicle_Collisions_Mar_12_2025.csv"
            ),
        ),
        # Build Downtown Brooklyn street network and map data to nearest intersections
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
        # Sum total persons injured per intersection
        (
            "enrich_injuries",
            CreateEnricher()
            .with_data(
                group_by="nearest_intersection", values_from="NUMBER OF PERSONS INJURED"
            )
            .aggregate_with(
                method="sum", target="nodes", output_column="total_injuries"
            )
            .build(),
        ),
        # Sum total persons killed per intersection
        (
            "enrich_fatalities",
            CreateEnricher()
            .with_data(
                group_by="nearest_intersection", values_from="NUMBER OF PERSONS KILLED"
            )
            .aggregate_with(
                method="sum", target="nodes", output_column="total_fatalities"
            )
            .build(),
        ),
        # Enable interactive result visualization
        ("viz", InteractiveVisualiser()),
    ]
)


# In[4]:


data, graph, nodes, edges = pipeline.compose_transform(
    latitude_column_name="LATITUDE", longitude_column_name="LONGITUDE"
)


# In[5]:


# Visualise the enriched network on intersections (nodes)
viz = pipeline.visualise(
    result_columns=["total_injuries", "total_fatalities"],
    target="nodes",
    colormap="Reds",
    tile_provider="Cartodb dark_matter",
)
viz


# In[ ]:
