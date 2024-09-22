from aiogram.filters.callback_data import CallbackData


class BaseCallback(CallbackData, prefix='base_prefix'):
    data: str


class MainMenuCallback(BaseCallback, prefix="main_menu"):
    pass


class BackButtonCallback(BaseCallback, prefix="back"):
    pass


class CourseCallback(BaseCallback, prefix='course'):
    data: int


class CoursePricesCallback(BaseCallback, prefix='course_prices'):
    pass


class PayButtonCallback(BaseCallback, prefix='pay'):
    pass


class CoursePartCallback(BaseCallback, prefix='part'):
    pass


class DownloadPartCallback(BaseCallback, prefix='download'):
    pass


class CheckEmailCallback(BaseCallback, prefix='check_email'):
    pass


class EnterEmailCallback(BaseCallback, prefix='confirm_email'):
    pass

