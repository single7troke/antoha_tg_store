from pydantic import BaseModel, PositiveInt
from typing import Optional, Any, Dict


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
    prices: dict[str, str]
    description: Optional[str] = None
    extended: bool = False
    parts: Optional[Dict[int, str]] = {}
    options: Optional[list[CourseOption]] = []


class UserCourse(BaseModel):
    course: Course
    paid: bool = False
    promo_access: bool = False
    payment_ids: Dict[str, Optional[str]] = dict()


class User(BaseModel):
    courses: Dict[int, UserCourse] = dict()
    email: Optional[str] = None
    invite_link: Optional[str] = None
    tg_user_data: Optional[Dict[Any, Any]] = None
    # Todo добавить фичу с доступом к скачиванию без оплаты


class Link(BaseModel):
    created: int
