from urban_mapper.modules.loader.loader_factory import LoaderFactory


class LoaderMixin(LoaderFactory):
    def __init__(self):
        super().__init__()
