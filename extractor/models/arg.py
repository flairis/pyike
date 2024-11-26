from pydantic import BaseModel


class Arg(BaseModel):
    name: str
    type: str | None
    desc: str | None
