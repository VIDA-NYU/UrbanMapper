from functools import wraps
from pathlib import Path

from beartype import beartype


@beartype
def file_exists(attr_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            path = getattr(self, attr_name)
            if not Path(path).exists():
                raise FileNotFoundError(f"File '{path}' does not exist.")
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
