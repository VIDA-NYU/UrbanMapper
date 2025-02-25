import inspect
from functools import wraps
from beartype import beartype


@beartype
def require_arguments_not_none(
    *arg_names, error_msg=None, check_empty=False, types=None
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            for name in arg_names:
                value = bound_args.arguments[name]
                if value is None:
                    raise ValueError(error_msg or f"Argument '{name}' cannot be None.")
                if check_empty and hasattr(value, "__len__") and len(value) == 0:
                    raise ValueError(error_msg or f"Argument '{name}' cannot be empty.")
                if types and not isinstance(value, types):
                    raise TypeError(
                        error_msg or f"Argument '{name}' must be one of {types}"
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator
