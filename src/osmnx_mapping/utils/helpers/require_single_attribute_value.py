from functools import wraps
from typing import Callable, Any
from beartype import beartype


@beartype
def require_single_attribute_value(attr_name: str, param_name: str, error_msg: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            new_value = kwargs.get(param_name, args[0] if args else None)
            if new_value is None:
                raise ValueError(f"Parameter '{param_name}' must be provided.")
            current_value = getattr(self, attr_name, None)
            if current_value is not None and current_value != new_value:
                raise ValueError(error_msg.format(current=current_value, new=new_value))
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
