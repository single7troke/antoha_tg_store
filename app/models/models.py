from pydantic import BaseModel, PositiveInt
from typing import Optional, Any


class Base(BaseModel):
    id: PositiveInt


class Course(Base):
    name: str
    price: str
    description: Optional[str] = None


class UserCourse(BaseModel):
    course: Course
    payment_link: str | None = None
    payment_data: Optional[dict[Any, Any]] = None


class User(BaseModel):
    courses: dict[int, UserCourse] = dict()
