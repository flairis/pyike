import inspect
import json
import pkgutil
import re
import time
from types import FunctionType, ModuleType
from typing import List

import ray
from docstring_parser import parse
from pydantic import BaseModel
from tqdm import tqdm

# ike init
# ike dev
# ike build
# ike deploy
from .models import ClassDefinition, FunctionDefinition, extract_class, extract_func

# start_time = time.time()
# extract(ray.data.range)
# print("--- %s seconds ---" % (time.time() - start_time))


def extract_definitions(
    module: ModuleType,
) -> List[FunctionDefinition | ClassDefinition]:
    names = getattr(module, "__all__", [])

    for name in tqdm(names):
        try:
            obj = getattr(module, name)
        except AttributeError:
            print("Failed to get", name)
            continue
        if isinstance(obj, FunctionType):
            definition = extract_func(obj)

    if package.__file__ is None:
        return []  # When does this happen?

    # The last part is the `__init__.py` file
    package_dir = "/".join(package.__file__.split("/")[:-1])
    for module in pkgutil.iter_modules([package_dir]):
        if not module.ispkg:
            continue

        module_name = x.__name__ + "." + module.name

        subpackage = importlib.import_module(module_name)
        extract_definitions(subpackage)

    return []


import os
import types


def write_definitions(
    definitions: List[FunctionDefinition | ClassDefinition], path: str
) -> None:
    assert os.path.isdir(path), path

    for definition in definitions:
        filename = f"{definition.name}.json"
        with open(os.path.join(path, filename), "w") as f:
            # f"../markdoc-starter/public/.cache/{definition.name}.json", "w"
            f.write(json.dumps(definition.model_dump(), indent=4))


import importlib


def main(package_name: str):
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        # TODO: Raise helpful error.
        raise

    definitions = extract_definitions(package)
    write_definitions(definitions, path=...)
