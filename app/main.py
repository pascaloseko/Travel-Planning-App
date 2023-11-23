from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import flight_bookings, hotel_bookings, itinerary, trips, users

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]  # Add the origins of your frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(trips.router)
app.include_router(itinerary.router)
app.include_router(hotel_bookings.router)
app.include_router(flight_bookings.router)
