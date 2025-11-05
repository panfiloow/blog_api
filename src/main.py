from fastapi import FastAPI
from src.routers.users import router as user_router

app = FastAPI(title="Blog API")
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Blog API!"}

