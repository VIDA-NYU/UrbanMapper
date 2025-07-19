import urban_mapper as um
import pytest


# @pytest.mark.skip()
class TestEnricherFactory:
    """
    It tests a EnricherFactory class.

    """

    enricher = um.UrbanMapper().enricher
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
        enricher = (
            self.enricher.with_data(group_by="borocode")
            .count_by(output_column="count_out")
            .build()
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Sum values
    """
        enricher = (
            self.enricher.with_data(group_by="OBJECTID", values_from="humps")
            .aggregate_by(method="sum", output_column="sum_out")
            .build()
        )
        assert enricher.enrich(self.data_speed_hump, self.layer) is not None

        """
        Minimum value
    """
        enricher = (
            self.enricher.with_data(group_by="borocode", values_from="gini")
            .aggregate_by(method="min", output_column="min_out")
            .build()
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Maximum value
    """
        enricher = (
            self.enricher.with_data(group_by="borocode", values_from="gini")
            .aggregate_by(method="max", output_column="max_out")
            .build()
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Mean value
    """
        enricher = (
            self.enricher.with_data(group_by="borocode", values_from="gini")
            .aggregate_by(method="mean", output_column="mean_out")
            .build()
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

        """
        Median value
    """
        enricher = (
            self.enricher.with_data(group_by="borocode", values_from="gini")
            .aggregate_by(method="median", output_column="median_out")
            .build()
        )
        assert enricher.enrich(self.data_neigborhood, self.layer) is not None

    def test_preview(self):
        enricher = (
            self.enricher.with_data(group_by="borocode", values_from="gini")
            .aggregate_by(method="median", output_column="median_out")
            .build()
        )

        assert enricher.preview(format="ascii") is not None

        assert enricher.preview(format="json") is not None
