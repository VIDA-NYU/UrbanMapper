class LazyMixin:
    def __init__(self, owner, name, mixin_cls):
        self.owner = owner
        self.name = name
        self.mixin_cls = mixin_cls
        self._instance = None
        self._last_params = None
        self._instantiating = False

    def _instantiate(self, *args, **kwargs):
        if self._instantiating:
            raise RecursionError("Recursive instantiation detected in LazyMixin")
        self._instantiating = True
        try:
            if args or kwargs:
                if self._instance is not None:
                    del self._instance
                    self._instance = None
                self._instance = self.mixin_cls(*args, **kwargs)
                self._last_params = (args, kwargs)
            elif self._instance is None:
                self._instance = self.mixin_cls()
                self.owner._instances[self.name] = self._instance
            return self._instance
        finally:
            self._instantiating = False

    def __call__(self, *args, **kwargs):
        return self._instantiate(*args, **kwargs)

    def __getattr__(self, attr):
        instance = self._instantiate()
        return getattr(instance, attr)
