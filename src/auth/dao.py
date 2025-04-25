from db.base_dao import BaseDAO
from .models import Token


class TokenDAO(BaseDAO):
    model = Token

