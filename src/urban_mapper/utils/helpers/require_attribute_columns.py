from functools import wraps
from beartype import beartype
import inspect


@beartype
def require_attribute_columns(data_arg_name: str, attr_names: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            data = bound_args.arguments[data_arg_name]
            if data is None:
                raise ValueError(f"Argument '{data_arg_name}' cannot be None")

            required_columns = [getattr(self, attr_name) for attr_name in attr_names]
            missing = [col for col in required_columns if col not in data.columns]
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
