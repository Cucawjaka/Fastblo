from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, delete, select

from db.base_dao import BaseDAO
from .models import Token


class TokenDAO(BaseDAO):
    model = Token

