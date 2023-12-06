import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.dependencies import get_current_user
from app.internal.hotel_bookings import HotelBookingQueries, HotelBookings
from app.internal.supadb import SupabaseClient

router = APIRouter(
    prefix="/api/v1",
    tags=["hotel_bookings"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


def get_hb_queries() -> HotelBookingQueries:
    return HotelBookingQueries(SupabaseClient())


@router.post("/protected/{trip_id}/hotel-bookings")
async def create_trip_hotel_booking(
    request: Request,
    trip_id,
    hb_queries: HotelBookingQueries = Depends(get_hb_queries),
):
    try:
        request_body = await request.body()
        request_data = request_body.decode("utf-8")

        hb_data = json.loads(request_data)
        validated_hb = HotelBookings.model_validate(hb_data)

        result = hb_queries.create_trip_hotel_booking(validated_hb, trip_id)
        if result["error"]:
            handle_error(result["error"], "error creating hotel booking")
        hb_id = result["data"][1][0]["id"]
        return {
            "hotel_booking_id": hb_id,
            "message": "Hotel Booking created successfully",
        }
    except ValidationError as e:
        return JSONResponse(content={"detail": str(e)}, status_code=400)


@router.get("/protected/{trip_id}/hotel-bookings")
async def get_trip_hotel_bookings(
    trip_id, hb_queries: HotelBookingQueries = Depends(get_hb_queries)
):
    result = hb_queries.get_trip_hotel_bookings(trip_id)
    if result["error"]:
        handle_error(result["error"], "error getting trip's hotel bookings")
    return result["data"]


def handle_error(error, error_message):
    if error:
        raise HTTPException(status_code=500, detail=f"{error_message}: {error}")
