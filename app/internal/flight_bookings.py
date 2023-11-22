from datetime import datetime

from pydantic import BaseModel

from app.internal.supadb import SupabaseClient


class FlightBookings(BaseModel):
    airline: str
    flight_number: str
    departure_date: datetime
    arrival_date: datetime


class FlightBookingQueries:
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client

    def create_trip_flight_booking(self, fb: FlightBookings, trip_id: int) -> dict:
        try:
            data, count = (
                self.supabase_client.client.table("flight_bookings")
                .insert(
                    [
                        {
                            "trip_id": trip_id,
                            "airline": fb.airline,
                            "flight_number": fb.flight_number,
                            "departure_date": fb.departure_date.isoformat(),
                            "arrival_date": fb.arrival_date.isoformat(),
                        }
                    ]
                )
                .execute()
            )

            return {"data": data, "error": None}
        except Exception as e:
            return {"data": None, "error": str(e)}

    def get_trip_flight_bookings(self, trip_id: int):
        try:
            response = (
                self.supabase_client.client.table("flight_bookings")
                .select("*")
                .eq("trip_id", trip_id)
                .execute()
            )
            return {"data": response, "error": None}
        except Exception as e:
            return {"data": None, "error": e}
