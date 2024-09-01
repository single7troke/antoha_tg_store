from pydantic import BaseModel, PositiveInt
from typing import Optional, Any, Dict


class Base(BaseModel):
    id: PositiveInt


class CourseOption(BaseModel):
    name: str
    price: str
    payed: bool
    description: str
    payment_link: Optional[str] = None
    payment_data: Optional[Dict[Any, Any]] = {}


class Course(Base):
    name: str
    prices: dict[str, str]
    description: Optional[str] = None
    extended: bool = False
    parts: Optional[Dict[int, str]] = {}
    options: Optional[list[CourseOption]] = []


class UserCourse(BaseModel):
    course: Course
    payed: bool = False
    payment_links: Optional[dict[str, Optional[str]]] = {}
    payments_data: Optional[Dict[str, Optional[Dict[Any, Any]]]] = {}


class User(BaseModel):
    courses: Dict[int, UserCourse] = dict()


class Link(BaseModel):
    created: int
