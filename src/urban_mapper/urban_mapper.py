from beartype import beartype
from urban_mapper.config import DEFAULT_CRS
from urban_mapper.config.container import container
from urban_mapper.utils import LazyMixin
import sys
from loguru import logger


class UrbanMapper:
    @beartype
    def __init__(
        self, coordinate_reference_system: str = DEFAULT_CRS, debug: str = None
    ):
        self.coordinate_reference_system = coordinate_reference_system
        self._instances = {}
        self._mixin_classes = container.mixin_classes()

        logger.remove()

        if debug is None:
            logger.add(
                sys.stderr,
                level="CRITICAL",
                format="<green>{time:YYYY-MM-DD HH:mm}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True,
            )
        else:
            debug_levels = {
                "LOW": "DEBUG_LOW",
                "MID": "DEBUG_MID",
                "HIGH": "DEBUG_HIGH",
            }
            if debug not in debug_levels:
                raise ValueError(
                    f"Invalid debug level: {debug}. Choose from {list(debug_levels.keys())} or None"
                )
            logger.add(
                sys.stderr,
                level=debug_levels[debug],
                format="<green>{time:YYYY-MM-DD HH:mm}</green> | {level.icon} <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True,
            )

    def __getattr__(self, name):
        if name in self._mixin_classes:
            if name in self._instances:
                return self._instances[name]
            proxy = LazyMixin(self, name, self._mixin_classes[name])
            self._instances[name] = proxy
            return proxy
        raise AttributeError(
            f"UrbanMapper has no mixin '{name}', maybe update the config yaml file?"
        )
