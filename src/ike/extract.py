import importlib
import json
import logging
import os
import pkgutil
from types import FunctionType, ModuleType
from typing import Iterable

from .models import PyClass, PyFunc, extract_func

logger = logging.getLogger(__name__)

PyObj = PyClass | PyFunc


def extract_definitions(module: ModuleType) -> Iterable[PyObj]:
    names = getattr(module, "__all__", [])
    for name in names:
        try:
            obj = getattr(module, name)
        except AttributeError:
            logger.warning(f"Failed to get '{name}' from '{module.__name__}'")
            continue
        if isinstance(obj, FunctionType):
            yield extract_func(obj)

    for sub_module in _iter_submodules(module):
        yield from extract_definitions(sub_module)


def _iter_submodules(package: ModuleType) -> Iterable[ModuleType]:
    if not _is_package(package):
        return

    for module_info in pkgutil.iter_modules(package.__path__):
        module_name = package.__name__ + "." + module_info.name
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            logger.warning(f"Couldn't import '{module_name}'")
            continue

        yield module


def _is_package(module: ModuleType) -> bool:
    return hasattr(module, "__path__")


def write_definition(definition: PyObj, path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    filename = f"{definition.name}.json"
    with open(os.path.join(path, filename), "w") as f:
        logger.debug(f"Writing '{f.name}'")
        f.write(json.dumps(definition.model_dump(), indent=4))
