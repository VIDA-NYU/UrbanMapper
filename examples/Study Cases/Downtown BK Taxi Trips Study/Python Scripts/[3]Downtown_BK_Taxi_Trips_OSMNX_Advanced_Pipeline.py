#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import osmnx_mapping as oxm
from osmnx_mapping.pipeline import UrbanPipeline
from osmnx_mapping.modules.loader import CSVLoader
from osmnx_mapping.modules.preprocessing import CreatePreprocessor
from osmnx_mapping.modules.enricher import CreateEnricher
from osmnx_mapping.modules.visualiser import InteractiveVisualiser
from osmnx_mapping.modules.network import CreateNetwork


# In[ ]:


collisions_study = oxm.OSMNxMapping()


# In[ ]:


pipeline = UrbanPipeline(
    [
        # Load taxi trip data from a CSV file
        ("load", CSVLoader(file_path="./../../../data/TAXIS/csv/taxisvis1M.csv")),
        # Build a street network for Downtown Brooklyn and map pickup/dropoff points to nodes
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
        # Remove rows with missing pickup coordinates
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
        # Remove rows with missing dropoff coordinates
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
        # Filter data to keep only points within the network's bounding box
        (
            "filter",
            CreatePreprocessor().with_filter(filter_type="BoundingBoxFilter").build(),
        ),
        # Count the number of pickups per node and enrich both nodes and edges
        (
            "enrich_pickups",
            CreateEnricher()
            .with_data(group_by="pickup_node")
            .count_by(target="both", output_column="pickup_count")
            .build(),
        ),
        # Count the number of dropoffs per node and enrich both nodes and edges
        (
            "enrich_dropoffs",
            CreateEnricher()
            .with_data(group_by="dropoff_node")
            .count_by(target="both", output_column="dropoff_count")
            .build(),
        ),
        # Calculate the average fare amount per pickup node and enrich both nodes and edges
        (
            "enrich_fare_amount",
            CreateEnricher()
            .with_data(group_by="pickup_node", values_from="fare_amount")
            .aggregate_with(
                method="mean", target="both", output_column="avg_fare_amount"
            )
            .build(),
        ),
        # Enable interactive visualization of the results
        ("viz", InteractiveVisualiser()),
    ]
)


# In[ ]:


data, graph, nodes, edges = pipeline.compose_transform(
    latitude_column_name="pickup_latitude", longitude_column_name="pickup_longitude"
)


# In[ ]:


viz = pipeline.visualise(
    result_columns=["pickup_count", "dropoff_count", "avg_fare_amount"],
    target="edges",
    colormap="Blues",
    tile_provider="Cartodb dark_matter",
)
viz


# In[ ]:


viz = pipeline.visualise(
    result_columns=["pickup_count", "dropoff_count", "avg_fare_amount"],
    target="nodes",
    colormap="Blues",
    tile_provider="Cartodb dark_matter",
)
viz


# In[ ]:


# In[ ]:
