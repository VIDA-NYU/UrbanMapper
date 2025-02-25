from functools import wraps
from beartype import beartype


@beartype
def require_attributes_not_none(*attr_names, error_msg=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for name in attr_names:
                if not hasattr(self, name):
                    raise AttributeError(
                        f"Attribute '{name}' is missing on {self.__class__.__name__}"
                    )
                if getattr(self, name) is None:
                    if error_msg:
                        raise ValueError(error_msg)
                    else:
                        raise ValueError(
                            f"Attribute '{name}' is None on {self.__class__.__name__}"
                        )
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
