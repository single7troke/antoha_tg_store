from pydantic import BaseModel, PositiveInt
from typing import Optional, Any, Dict, List


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
    prices: Dict[str, str]
    description: Optional[str] = None
    extended: bool = False
    parts: Optional[Dict[int, str]] = {}
    options: Optional[List[CourseOption]] = []


class UserCourse(BaseModel):
    course: Course
    payed: bool = False
    payment_links: Optional[Dict[str, Optional[str]]] = {}
    payments_data: Optional[Dict[str, Optional[Dict[Any, Any]]]] = {}


class User(BaseModel):
    courses: Dict[int, UserCourse] = dict()
