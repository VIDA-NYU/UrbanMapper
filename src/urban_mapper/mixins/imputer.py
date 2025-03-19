from urban_mapper.modules.imputer import ImputerFactory


class ImputerMixin(ImputerFactory):
    def __init__(self):
        super().__init__()
