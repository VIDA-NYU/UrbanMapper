from urban_mapper.modules.enricher.enricher_factory import EnricherFactory


class EnricherMixin(EnricherFactory):
    def __init__(self):
        super().__init__()
