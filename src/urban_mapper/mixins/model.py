from urban_mapper.modules.model.model_factory import ModelFactory


class ModelMixin(ModelFactory):
    def __init__(self):
        super().__init__()
