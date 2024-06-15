from .keyboard import COURSES
from models.models import Course


async def get_list() -> list[Course]:
    return COURSES


async def get(course_id: int) -> Course | None:
    for course in COURSES:
        if course.id == course_id:
            return course
