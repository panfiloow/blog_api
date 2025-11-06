from fastapi import FastAPI
from src.routers.users import router as user_router
from src.routers.posts import router as post_router
from src.routers.comments import router as comment_router

app = FastAPI(title="Blog API")
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Blog API!"}

