from pydantic import BaseModel, PositiveInt
from typing import Optional


class Base(BaseModel):
    id: PositiveInt


class Course(Base):
    name: str
    price: PositiveInt
    description: Optional[str] = None
