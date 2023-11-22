from datetime import datetime

from pydantic import BaseModel

from app.internal.supadb import SupabaseClient


class HotelBookings(BaseModel):
    hotel_name: str
    check_in_date: datetime
    check_out_date: datetime


class HotelBookingQueries:
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client

    def create_trip_hotel_booking(self, hb: HotelBookings, trip_id: int) -> dict:
        try:
            data, count = (
                self.supabase_client.client.table("hotel_bookings")
                .insert(
                    [
                        {
                            "trip_id": trip_id,
                            "hotel_name": hb.hotel_name,
                            "check_in_date": hb.check_in_date.isoformat(),
                            "check_out_date": hb.check_out_date.isoformat(),
                        }
                    ]
                )
                .execute()
            )

            return {"data": data, "error": None}
        except Exception as e:
            return {"data": None, "error": str(e)}

    def get_trip_hotel_bookings(self, trip_id: int):
        try:
            response = (
                self.supabase_client.client.table("hotel_bookings")
                .select("*")
                .eq("trip_id", trip_id)
                .execute()
            )
            return {"data": response, "error": None}
        except Exception as e:
            return {"data": None, "error": e}
