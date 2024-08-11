from pydantic import BaseModel, PositiveInt
from typing import Optional, Any, Dict


class Base(BaseModel):
    id: PositiveInt


class Course(Base):
    name: str
    price: str
    description: Optional[str] = None
    parts: Optional[Dict[int, str]] = None


class UserCourse(BaseModel):
    course: Course
    payment_link: Optional[str] = None
    payment_data: Optional[Dict[Any, Any]] = {}


class User(BaseModel):
    courses: Dict[int, UserCourse] = dict()


class Link(BaseModel):
    created: int
