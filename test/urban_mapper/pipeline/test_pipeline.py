import urban_mapper as um
import copy
import pytest
import os
from urban_mapper.pipeline import UrbanPipeline


# @pytest.mark.skip()
class TestUrbanPipeline:
    """
    It tests a UrbanPipeline class.

    """

    place = "Downtown, Brooklyn, New York, USA"
    neighborhoods_path = "test/data_files/small_nyc_neighborhoods.csv"
    education_path = "test/data_files/small_nyc_education.csv"
    pipe_path = "test/data_files/simple_pipeline.dill"
    tmp_path = "test/data_files/tmp"

    layer = (
        um.UrbanMapper()
        .urban_layer.with_type("streets_roads")
        .from_place(place, network_type="drive")
        .with_mapping(geometry_column="geometry", output_column="mapping_output")
        .build()
    )

    loader1 = (
        um.UrbanMapper()
        .loader.from_file(neighborhoods_path)
        .with_columns(geometry_column="geometry")
        .build()
    )
    loader2 = (
        um.UrbanMapper()
        .loader.from_file(education_path)
        .with_columns(geometry_column="geometry")
        .with_crs(("EPSG:2263", "EPSG:4326"))
        .build()
    )

    imputer = (
        um.UrbanMapper()
        .imputer.with_type("SimpleGeoImputer")
        .on_columns(geometry_column="geometry")
        .build()
    )

    filter = um.UrbanMapper().filter.with_type("BoundingBoxFilter").build()

    enricher1 = (
        um.UrbanMapper()
        .enricher.with_data(
            group_by="mapping_output", values_from="gini", data_id="loader1"
        )
        .aggregate_by(method="min", output_column="min_out")
        .build()
    )
    enricher2 = (
        um.UrbanMapper()
        .enricher.with_data(
            group_by="mapping_output", values_from="gini", data_id="loader1"
        )
        .aggregate_by(method="max", output_column="max_out")
        .build()
    )
    enricher3 = (
        um.UrbanMapper()
        .enricher.with_data(
            group_by="mapping_output", values_from="population", data_id="loader2"
        )
        .aggregate_by(method="sum", output_column="sum_out")
        .build()
    )

    def test_init(self):
        """
        Pipeline with one dataset
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
            ]
        )

        assert pipeline is not None

        """
        Pipeline with many datasets
    """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )

        assert pipeline is not None

    def test_get_step(self):
        """
        Pipeline with many datasets
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )

        for name in pipeline.get_step_names():
            """
        __getitem__
      """
            assert pipeline[name] is not None

            """
        get_step
      """
            assert pipeline.get_step(name) is not None

            # TODO: check why it's not working
            # step = pipeline.name_steps

    def test_compose(self):
        """
        Pipeline with one dataset
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
            ]
        )

        assert pipeline.compose() is not None

        """
        Pipeline with many datasets
    """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )

        assert pipeline.compose() is not None

    def test_transform(self):
        """
        Pipeline with one dataset
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
            ]
        )

        assert pipeline.compose().transform() is not None

        """
        Pipeline with many datasets
    """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )

        assert pipeline.compose().transform() is not None

    def test_compose_transform(self):
        """
        Pipeline with one dataset
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
            ]
        )

        assert pipeline.compose_transform() is not None

        """
        Pipeline with many datasets
    """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )

        assert pipeline.compose_transform() is not None

    def test_visualize(self):
        pass

    def test_save(self):
        """
        Pipeline with many datasets
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )
        pipeline.compose_transform()

        assert pipeline.save(os.path.join(self.tmp_path, "pipeline.dill")) is None

    def test_load(self):
        pipeline = UrbanPipeline.load(self.pipe_path)

        assert pipeline is not None

    def test_preview(self):
        """
        Pipeline with many datasets
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )

        assert pipeline.preview("ascii") is None

        assert pipeline.preview("json") is None

    def test_to_jgis(self):
        """
        Pipeline with many datasets
        """
        pipeline = UrbanPipeline(
            [
                ("urban_layer", copy.deepcopy(self.layer)),
                ("loader1", self.loader1),
                ("loader2", self.loader2),
                ("imputer", self.imputer),
                ("filter", self.filter),
                ("enricher1", self.enricher1),
                ("enricher2", self.enricher2),
                ("enricher3", self.enricher3),
            ]
        )
        pipeline.compose_transform()

        file_path = os.path.join(self.tmp_path, "map.jgis")

        if os.path.isfile(file_path):
            os.remove(file_path)

        assert pipeline.to_jgis(file_path) is None
