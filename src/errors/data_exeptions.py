class NotFoundError(Exception):
    def __init__(self, msg: str | None = None):
        self.msg = msg


class UserNotFoundError(NotFoundError):
    pass


class PostNotFoundError(NotFoundError):
    pass


class Duplicate(Exception):
    def __init__(self, msg: str | None = None):
        self.msg = msg


class TransactionError(Exception):
    """Ошибка транзакции базы данных"""
    pass


class IncorrectFilterAppliedError(Exception):
    """Обновляется слишком много записей"""
    def __init__(self, msg: str | None = None):
        self.msg = msg