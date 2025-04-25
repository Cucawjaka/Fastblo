from db.base_dao import BaseDAO
from db.models import Post



class PostDAO(BaseDAO):
    model = Post

    