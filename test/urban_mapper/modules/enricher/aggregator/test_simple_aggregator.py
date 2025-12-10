import urban_mapper as um
from urban_mapper.modules.enricher import SimpleAggregator, AGGREGATION_FUNCTIONS
import pytest


# @pytest.mark.skip()
class TestSimpleAggregator:
    """
    It tests a SimpleAggregator class.

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

    def test_aggregate(self):
        """
        Sum values
        """
        aggregator = SimpleAggregator(
            group_by_column="OBJECTID",
            value_column="humps",
            aggregation_function=AGGREGATION_FUNCTIONS["sum"],
        )
        assert aggregator.aggregate(self.data_speed_hump) is not None

        """
        Minimum value
    """
        aggregator = SimpleAggregator(
            group_by_column="borocode",
            value_column="gini",
            aggregation_function=AGGREGATION_FUNCTIONS["min"],
        )
        assert aggregator.aggregate(self.data_neigborhood) is not None

        """
        Maximum value
    """
        aggregator = SimpleAggregator(
            group_by_column="borocode",
            value_column="gini",
            aggregation_function=AGGREGATION_FUNCTIONS["max"],
        )
        assert aggregator.aggregate(self.data_neigborhood) is not None

        """
        Mean value
    """
        aggregator = SimpleAggregator(
            group_by_column="borocode",
            value_column="gini",
            aggregation_function=AGGREGATION_FUNCTIONS["mean"],
        )
        assert aggregator.aggregate(self.data_neigborhood) is not None

        """
        Median value
    """
        aggregator = SimpleAggregator(
            group_by_column="borocode",
            value_column="gini",
            aggregation_function=AGGREGATION_FUNCTIONS["median"],
        )
        assert aggregator.aggregate(self.data_neigborhood) is not None
