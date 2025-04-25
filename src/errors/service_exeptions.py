class UserInactiveError(Exception):
    """Неактивный пользователь"""
    def __init__(self, msg: str | None = None) -> None:
        self.msg = msg


class InvalidCredentialsError(Exception):
    """Неправильный логин или пароль"""
    def __init__(self, msg: str | None = None) -> None:
        self.msg = msg


class UserDeletionIntegrityError(Exception):
    """Ошика удаления большого количества пользователей"""
    def __init__(self, msg: str | None = None) -> None:
        self.msg = msg


class PermissionDenied(Exception):
    """Запрещенное действие"""
    def __init__(self, msg: str | None = None) -> None:
        self.msg = msg


class InvalidTokenTypeError(Exception):
    """Некорректный тип токена"""
    def __init__(self, msg: str | None = None) -> None:
        self.msg = msg


class TokenRefreshError(Exception):
    """Ошибка изменения токенов"""
    def __init__(self, msg: str | None = None) -> None:
        self.msg = msg


# class CastomValidationError(Exception):
#     def __init__(self, msg: str | None = None) -> None:
#         self.msg = msg


# class PasswordValidationError(CastomValidationError):
#     pass


