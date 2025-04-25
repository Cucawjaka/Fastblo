import uvicorn
from fastapi import FastAPI

from auth.router import router as auth_router
from api.post_router import router as post_router
from api.user_router import router as user_router
from errors.exception_handler import register_exception_handler




app = FastAPI(title="FastBlo")

register_exception_handler(app=app)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
