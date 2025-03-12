#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import osmnx_mapping as oxm
from osmnx_mapping.pipeline import UrbanPipeline
from osmnx_mapping.modules.loader import CSVLoader
from osmnx_mapping.modules.preprocessing import CreatePreprocessor
from osmnx_mapping.modules.enricher import CreateEnricher
from osmnx_mapping.modules.visualiser import InteractiveVisualiser
from osmnx_mapping import CreateNetwork


# In[ ]:


taxi_study = oxm.OSMNxMapping()


# In[ ]:


pipeline = UrbanPipeline(
    [
        # Step 1: Load taxi trip data from CSV
        ("load", CSVLoader(file_path="./../../../data/TAXIS/csv/taxisvis1M.csv")),
        # Step 2: Build Downtown Brooklyn street network and map pickups/dropoffs to nodes
        (
            "network",
            CreateNetwork()
            .with_place("Downtown, Brooklyn, New York, USA", network_type="drive")
            .with_mapping(
                mapping_type="node",
                longitude_column_name="pickup_longitude",
                latitude_column_name="pickup_latitude",
                output_column="pickup_node",
            )
            .with_mapping(
                mapping_type="node",
                longitude_column_name="dropoff_longitude",
                latitude_column_name="dropoff_latitude",
                output_column="dropoff_node",
            )
            .build(),
        ),
        # Step 3: Impute missing pickup coordinates
        (
            "impute_pickup",
            CreatePreprocessor()
            .with_imputer(
                imputer_type="SimpleGeoImputer",
                latitude_column_name="pickup_latitude",
                longitude_column_name="pickup_longitude",
            )
            .build(),
        ),
        # Step 4: Impute missing dropoff coordinates
        (
            "impute_dropoff",
            CreatePreprocessor()
            .with_imputer(
                imputer_type="SimpleGeoImputer",
                latitude_column_name="dropoff_latitude",
                longitude_column_name="dropoff_longitude",
            )
            .build(),
        ),
        # Step 5: Filter data to the network's bounding box
        (
            "filter",
            CreatePreprocessor().with_filter(filter_type="BoundingBoxFilter").build(),
        ),
        # Step 6: Enrich with pickup counts
        (
            "enrich_pickups",
            CreateEnricher()
            .with_data(group_by="pickup_node")
            .count_by(
                target="both",  # Enrich both nodes and edges
                output_column="pickup_count",
            )
            .build(),
        ),
        # Step 7: Enrich with dropoff counts
        (
            "enrich_dropoffs",
            CreateEnricher()
            .with_data(group_by="dropoff_node")
            .count_by(
                target="both",  # Enrich both nodes and edges
                output_column="dropoff_count",
            )
            .build(),
        ),
        # Step 8: Viz enriched network
        ("viz", InteractiveVisualiser()),
    ]
)


# In[ ]:


data, graph, nodes, edges = pipeline.compose_transform(
    latitude_column_name="pickup_latitude",  # Innapropriate, will change in Urban Mapper
    longitude_column_name="pickup_longitude",  # Innapropriate, will change in Urban Mapper
)


# In[ ]:


# Visualise the enriched network on intersections (nodes)
viz = pipeline.visualise(
    result_columns=["pickup_count", "dropoff_count"],
    target="edges",
    colormap="Reds",
    tile_provider="Cartodb dark_matter",
)
viz


# In[ ]:


# Visualise the enriched network on intersections (nodes)
viz = pipeline.visualise(
    result_columns=["pickup_count", "dropoff_count"],
    target="nodes",
    colormap="Reds",
    tile_provider="Cartodb dark_matter",
)
viz


# In[ ]:
