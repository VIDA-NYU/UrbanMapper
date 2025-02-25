from functools import wraps
from typing import Callable, List, Any
from beartype import beartype


@beartype
def require_attributes(required_attrs: List[str]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            for attr_name in required_attrs:
                if not hasattr(self, attr_name):
                    raise AttributeError(
                        f"Required attribute '{attr_name}' is missing on {self.__class__.__name__}"
                    )
                value = getattr(self, attr_name)

                if value is None:
                    raise AttributeError(
                        f"Required attribute '{attr_name}' is None on {self.__class__.__name__}"
                    )

                if isinstance(value, str) and len(value) == 0:
                    raise AttributeError(
                        f"Required attribute '{attr_name}' is an empty string on {self.__class__.__name__}"
                    )

                if isinstance(value, list) and len(value) == 0:
                    raise AttributeError(
                        f"Required attribute '{attr_name}' is an empty list on {self.__class__.__name__}"
                    )
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
