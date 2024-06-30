from typing import Union


class CacheKeyConstructor:
    separator: str = ':::'
    tg_id: str = 'tg_id'
    payment_problems: str = 'payment_problems'

    @classmethod
    def get_user_payment(cls, user_id: Union[int, str], payment_id: str):
        return f'{user_id}{cls.separator}{payment_id}'

    @classmethod
    def tg_id_key(cls, user_id: Union[int, str]):
        return f'{cls.tg_id}{cls.separator}{user_id}'

    @classmethod
    def tg_id_payment_problems_key(cls, user_id: Union[int, str]):
        return f'{cls.tg_id_key(user_id)}{cls.separator}{cls.payment_problems}'
