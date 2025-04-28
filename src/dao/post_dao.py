from src.db.base_dao import BaseDAO
from src.db.models import Post


class PostDAO(BaseDAO):
    model = Post

    