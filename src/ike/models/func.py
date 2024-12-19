import inspect
from types import FunctionType
from typing import List

from docstring_parser import parse
from pydantic import BaseModel

from .arg import Arg
from .example import Example


class PyFunc(BaseModel):
    name: str
    signature: str
    summary: str | None
    desc: str | None
    args: List[Arg]
    returns: str | None
    examples: List[Example]


def extract_func(func: FunctionType) -> PyFunc:
    assert isinstance(func, FunctionType), func

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

    return PyFunc(
        name=name,
        signature=signature,
        summary=summary,
        desc=desc,
        args=args,
        returns=returns,
        examples=examples,
    )
