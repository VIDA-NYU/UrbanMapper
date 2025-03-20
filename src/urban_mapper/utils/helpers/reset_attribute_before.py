import abc
import functools
from urban_mapper import logger


def reset_attributes_before(attrs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            for attr in attrs:
                current_value = getattr(self, attr, None)

                if isinstance(current_value, str):
                    reset_value = None
                elif isinstance(current_value, dict):
                    reset_value = {} if current_value else current_value
                elif isinstance(current_value, list):
                    reset_value = [] if current_value else current_value
                elif isinstance(current_value, tuple):
                    reset_value = () if current_value else current_value
                elif isinstance(current_value, abc.ABCMeta):
                    reset_value = None if current_value else current_value
                elif isinstance(current_value, set):
                    reset_value = set() if current_value else current_value
                elif isinstance(current_value, bool):
                    reset_value = not current_value
                elif current_value is None:
                    reset_value = None
                else:
                    raise ValueError(
                        f"The following type is not supported for resetting: {type(current_value)}"
                    )

                if current_value != reset_value:
                    logger.log(
                        "DEBUG_MID",
                        f"Attribute '{attr}' is being overwritten from {current_value} to {reset_value}. "
                        f"Prior to most probably being set again by the method you are calling.",
                    )
                    setattr(self, attr, reset_value)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
