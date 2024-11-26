from pydantic import BaseModel


class Example(BaseModel):
    desc: str | None
    code: str
