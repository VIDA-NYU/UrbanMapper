from functools import wraps
from beartype import beartype
from typing import Callable, List, Optional
import inspect


@beartype
def require_dynamic_columns(
    data_arg_name: str,
    get_columns: Callable[[dict], List[str]],
    condition: Optional[Callable[[dict], bool]] = None,
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            if condition is None or condition(bound_args.arguments):
                data = bound_args.arguments[data_arg_name]
                if data is None:
                    raise ValueError(f"Argument '{data_arg_name}' cannot be None")
                required_columns = get_columns(bound_args.arguments)
                missing = [col for col in required_columns if col not in data.columns]
                if missing:
                    raise ValueError(f"Missing required columns: {', '.join(missing)}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
