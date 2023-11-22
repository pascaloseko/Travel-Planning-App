from fastapi import FastAPI

from app.routers import users, trips, itinerary

app = FastAPI()

app.include_router(users.router)
app.include_router(trips.router)
app.include_router(itinerary.router)
