from root_dir import ROOT_PATH
from shared.debugger import log
from pathlib import Path
import importlib


class Package:
    def __init__(self, path: Path, wrapper=lambda *a: lambda o: lambda *args: o(*args)):
        self.storage = {}
        self.wrapper = wrapper

        path = path.resolve()
        if not str(path).startswith(str(ROOT_PATH)):
            raise ValueError(f"Package path {path} is not inside root {ROOT_PATH}")

        self.path = path
        self.import_base = ".".join(path.relative_to(ROOT_PATH).parts)
        self.initialized = False

    def initialize(self):
        log('info', f"Initializing package {self.import_base}")
        for file in self.path.glob("*.py"):
            if file.name == "__init__.py":
                continue
            module_name = f"{self.import_base}.{file.stem}"
            log('info', f"Loading module {module_name}")
            importlib.import_module(module_name)

    def register(self, key: str, *args) -> callable:
        def decorator(obj):
            wrapped = self.wrapper(*args)(obj)
            self.storage[key] = wrapped
            return wrapped
        return decorator

    def resolve(self, key: str):
        if key not in self.storage:
            raise ValueError(f"Unknown package: {key}")
        return self.storage[key]
