from aiogram.filters.callback_data import CallbackData


class BaseCallback(CallbackData, prefix='base_prefix'):
    data: str


class MainMenuCallback(BaseCallback, prefix="main_menu"):
    pass


class BackButtonCallback(BaseCallback, prefix="back"):
    pass


class CatalogCallback(BaseCallback, prefix='catalog'):
    pass


class CourseCallback(BaseCallback, prefix='course'):
    data: int


class PayButtonCallback(BaseCallback, prefix='pay'):
    pass
