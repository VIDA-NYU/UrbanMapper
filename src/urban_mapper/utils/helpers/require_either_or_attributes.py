from functools import wraps
from beartype import beartype


@beartype
def require_either_or_attributes(attr_groups, error_msg=None):
    """
    Ensure that at least one group of attributes is fully set (not None).

    Args:
        attr_groups: List of attribute groups where all attributes in at least one group must be set.
        error_msg: Custom error message to raise if the condition is not met.

    Returns:
        Decorator for the function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for group in attr_groups:
                if all(
                    hasattr(self, attr) and getattr(self, attr) is not None
                    for attr in group
                ):
                    break
            else:
                raise ValueError(
                    error_msg
                    or f"At least one of the following attribute groups must be fully set: {attr_groups}"
                )
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
