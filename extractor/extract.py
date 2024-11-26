from types import FunctionType
from typing import List
import inspect
import ray
from pydantic import BaseModel
import re
from docstring_parser import parse
from types import ModuleType


class Arg(BaseModel):
    name: str
    type: str | None
    desc: str | None


class Example(BaseModel):
    desc: str | None
    code: str


class FunctionDefinition(BaseModel):
    name: str
    signature: str
    summary: str | None
    desc: str | None
    args: List[Arg]
    returns: str | None
    examples: List[Example]


class ClassDefinition(BaseModel):
    name: str
    signature: str
    summary: str | None
    desc: str | None
    args: List[Arg]
    examples: List[Example]
    methods: List[FunctionDefinition]


def extract_method(func: FunctionType):
    import inspect


def extract_class(cls: type):
    assert isinstance(cls, type), cls

    methods = inspect.getmembers(cls, predicate=inspect.isfunction)
    for name, method in methods:
        extract_func(method)


def extract_func(func: FunctionType):
    name = func.__module__ + "." + func.__qualname__
    signature = name + repr(inspect.signature(func))[len("<Signature ") : -len(">")]
    parsed = parse(func.__doc__)
    summary = parsed.short_description
    desc = parsed.long_description

    args = []
    for param in parsed.params:
        args.append(
            Arg(name=param.arg_name, type=param.type_name, desc=param.description)
        )
    returns = parsed.returns.description if parsed.returns else None

    examples = []
    for example in parsed.examples:
        examples.append(Example(desc=None, code=example.description))

    return FunctionDefinition(
        name=name,
        signature=signature,
        summary=summary,
        desc=desc,
        args=args,
        returns=returns,
        examples=examples,
    )


import time
import json

# start_time = time.time()
# extract(ray.data.range)
# print("--- %s seconds ---" % (time.time() - start_time))

from tqdm import tqdm

import pkgutil


def extract_all(x):
    items = getattr(x, "__all__", [])
    for name in tqdm(items):
        try:
            obj = getattr(x, name)
        except AttributeError:
            print("Failed to get", name)
            continue
        if isinstance(obj, FunctionType):
            func = obj
            definition = extract_func(func)
            print("Extracting function", definition.name)
            with open(
                f"../markdoc-starter/public/.cache/{definition.name}.json", "w"
            ) as f:
                f.write(json.dumps(definition.model_dump(), indent=4))

    path = "/".join(x.__file__.split("/")[:-1])
    for module in pkgutil.iter_modules([path]):
        if not module.ispkg:
            continue

        module_name = x.__name__ + "." + module.name
        import importlib

        sub_module = importlib.import_module(module_name)
        extract_all(sub_module)


extract_all(ray.data)
