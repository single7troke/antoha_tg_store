from typing import Union
from uuid import uuid4


class CacheKeyConstructor:
    separator: str = ':::'

    @classmethod
    def user(cls, user_id: Union[int, str]):
        return f'user{cls.separator}{user_id}'

    @classmethod
    def payment(cls, user_id: Union[int, str], payment_id: str):
        return f'payment{cls.separator}{user_id}{cls.separator}{payment_id}'

    @classmethod
    def payment_issues(cls, user_id: Union[int, str]):
        return f'payment_issues{cls.separator}{user_id}'

    @classmethod
    def link(cls, user_id: Union[int, str], course_id: int, course_part_id: int):
        return f'link{cls.separator}{user_id}{cls.separator}{course_id}{cls.separator}{course_part_id}'
