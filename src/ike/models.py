from enum import Enum
from typing import List

from pydantic import BaseModel


class PyObjType(str, Enum):
    CLASS = "class"
    FUNC = "func"


class PyArg(BaseModel):
    name: str
    type: str | None
    desc: str | None


class DocstringExample(BaseModel):
    desc: str | None
    code: str


class PyObj(BaseModel):
    name: str
    type: PyObjType
    summary: str | None
    desc: str | None
    examples: List[DocstringExample]


class PyFunc(PyObj):
    type: PyObjType = PyObjType.FUNC
    signature: str
    args: List[PyArg]
    returns: str | None


class PyClass(PyObj):
    type: PyObjType = PyObjType.CLASS
    signature: str
    args: List[PyArg]
    methods: List[PyFunc]
