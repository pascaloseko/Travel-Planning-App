import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.dependencies import get_current_user
from app.internal.flight_bookings import FlightBookingQueries, FlightBookings
from app.internal.supadb import SupabaseClient

router = APIRouter(
    prefix="/api/v1",
    tags=["flight_bookings"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


def get_fb_queries() -> FlightBookingQueries:
    return FlightBookingQueries(SupabaseClient())


@router.post("/protected/{trip_id}/flight-bookings")
async def create_trip_flight_booking(
    request: Request,
    trip_id,
    hb_queries: FlightBookingQueries = Depends(get_fb_queries),
):
    try:
        request_body = await request.body()
        request_data = request_body.decode("utf-8")

        fb_data = json.loads(request_data)
        validated_fb = FlightBookings.model_validate(fb_data)

        result = hb_queries.create_trip_flight_booking(validated_fb, trip_id)
        if result["error"]:
            handle_error(result["error"], "error creating flight booking for trip")
        fb_id = result["data"][1][0]["id"]
        return {
            "flight_booking_id": fb_id,
            "message": "Flight Booking created successfully",
        }
    except ValidationError as e:
        return JSONResponse(content={"detail": str(e)}, status_code=400)


@router.get("/protected/{trip_id}/flight-bookings")
async def get_trip_flight_bookings(
    trip_id, fb_queries: FlightBookingQueries = Depends(get_fb_queries)
):
    result = fb_queries.get_trip_flight_bookings(trip_id)
    if result["error"]:
        handle_error(result["error"], "error getting trip's flight bookings")
    return result["data"]


def handle_error(error, error_message):
    if error:
        raise HTTPException(status_code=500, detail=f"{error_message}: {error}")
