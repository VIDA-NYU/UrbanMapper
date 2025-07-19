import urban_mapper as um
from urban_mapper import SingleAggregatorEnricher
from urban_mapper.modules.enricher import (
    CountAggregator,
    SimpleAggregator,
    AGGREGATION_FUNCTIONS,
)
from urban_mapper.modules.enricher.factory import EnricherConfig
import pytest


# @pytest.mark.skip()
class TestSingleAggregatorEnricher:
    """
    It tests a SingleAggregatorEnricher class.

    """

    loader = um.UrbanMapper().loader

    file_path = "test/data_files/small_nyc_neighborhoods.csv"
    data_neigborhood = (
        loader.from_file(file_path).with_columns(geometry_column="geometry").load()
    )

    file_path = "test/data_files/small_VZV_Speed_Humps_with_LatLon.csv"
    data_speed_hump = (
        loader.from_file(file_path)
        .with_columns(geometry_column="the_geom")
        .with_map({"the_geom": "geometry"})
        .load()
    )

    config = EnricherConfig()

    # "Manhattan, New York, New York, USA"
    # "Brooklyn, New York, USA"

    layer = (
        um.UrbanMapper()
        .urban_layer.with_type("streets_roads")
        .from_place("Brooklyn, New York, USA")
        .build()
    )

    def test_enrich(self):
        """
        Grouping and couting rows
        """
        enricher = SingleAggregatorEnricher(
            aggregator=CountAggregator(group_by_column="borocode", count_function=len),
            output_column="count_out",
            config=self.config,
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Sum values
    """
        enricher = SingleAggregatorEnricher(
            aggregator=SimpleAggregator(
                group_by_column="OBJECTID",
                value_column="humps",
                aggregation_function=AGGREGATION_FUNCTIONS["sum"],
            ),
            output_column="sum_out",
            config=self.config,
        )
        assert enricher.enrich(self.data_speed_hump, self.layer) is not None

        """
        Minimum value
    """
        enricher = SingleAggregatorEnricher(
            aggregator=SimpleAggregator(
                group_by_column="borocode",
                value_column="gini",
                aggregation_function=AGGREGATION_FUNCTIONS["min"],
            ),
            output_column="min_out",
            config=self.config,
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Maximum value
    """
        enricher = SingleAggregatorEnricher(
            aggregator=SimpleAggregator(
                group_by_column="borocode",
                value_column="gini",
                aggregation_function=AGGREGATION_FUNCTIONS["max"],
            ),
            output_column="max_out",
            config=self.config,
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Mean value
    """
        enricher = SingleAggregatorEnricher(
            aggregator=SimpleAggregator(
                group_by_column="borocode",
                value_column="gini",
                aggregation_function=AGGREGATION_FUNCTIONS["mean"],
            ),
            output_column="max_out",
            config=self.config,
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Median value
    """
        enricher = SingleAggregatorEnricher(
            aggregator=SimpleAggregator(
                group_by_column="borocode",
                value_column="gini",
                aggregation_function=AGGREGATION_FUNCTIONS["median"],
            ),
            output_column="median_out",
            config=self.config,
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

    def test_preview(self):
        enricher = SingleAggregatorEnricher(
            aggregator=SimpleAggregator(
                group_by_column="borocode",
                value_column="gini",
                aggregation_function=AGGREGATION_FUNCTIONS["median"],
            ),
            output_column="median_out",
            config=self.config,
        )

        assert isinstance(enricher.preview(format="ascii"), str)

        assert isinstance(enricher.preview(format="json"), dict)
