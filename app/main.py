from fastapi import FastAPI

from app.routers import users, trips

app = FastAPI()

app.include_router(users.router)
app.include_router(trips.router)
