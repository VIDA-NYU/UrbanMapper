import urban_mapper as um
from urban_mapper.modules.enricher import CountAggregator
import pytest


# @pytest.mark.skip()
class TestCountAggregator:
    """
    It tests a CountAggregator class.

    """

    loader = um.UrbanMapper().loader

    file_path = "test/data_files/small_nyc_neighborhoods.csv"
    data_neigborhood = (
        loader.from_file(file_path).with_columns(geometry_column="geometry").load()
    )

    def test_aggregate(self):
        """
        Grouping and couting rows
        """
        aggregator = CountAggregator(group_by_column="borocode", count_function=len)
        assert aggregator.aggregate(self.data_neigborhood) is not None
