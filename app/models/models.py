from datetime import datetime

from pydantic import BaseModel, PositiveInt
from typing import Optional, Any, Dict, List


class Base(BaseModel):
    id: PositiveInt


class CourseOption(BaseModel):
    name: str
    price: str
    paid: bool
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
    paid: Optional[str] = None
    promo_access: bool = False
    payment_ids: Dict[str, str] = dict()
    captured_at: str = None


class User(BaseModel):
    courses: Dict[int, UserCourse] = dict()
    email: Optional[str] = None
    invite_link: Optional[str] = None
    tg_user_data: Optional[Dict[Any, Any]] = None
