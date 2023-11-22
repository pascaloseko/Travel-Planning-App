from fastapi import FastAPI

from app.routers import (flight_bookings, hotel_bookings, itinerary, trips,
                         users)

app = FastAPI()

app.include_router(users.router)
app.include_router(trips.router)
app.include_router(itinerary.router)
app.include_router(hotel_bookings.router)
app.include_router(flight_bookings.router)
