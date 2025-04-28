from src.db.base_dao import BaseDAO
from src.auth.models import Token


class TokenDAO(BaseDAO):
    model = Token

