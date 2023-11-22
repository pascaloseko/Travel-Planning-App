from datetime import datetime
from pydantic import BaseModel

from app.internal.supadb import SupabaseClient


class Trip(BaseModel):
    title: str
    start_date: str
    end_date: str


class TripQueries:
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client

    def create_trip(self, trip: Trip, user_id: int) -> dict:
        try:
            start_date = datetime.strptime(trip.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(trip.end_date, "%Y-%m-%d").date()

            data, count = (
                self.supabase_client.client.table("trips")
                .insert(
                    [
                        {
                            "user_id": user_id,
                            "title": trip.title,
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat(),
                        }
                    ]
                )
                .execute()
            )

            return {"data": data, "error": None}
        except Exception as e:
            return {"data": None, "error": str(e)}

    def get_user_trips(self, user_id: int):
        try:
            response = (
                self.supabase_client.client.table("trips")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            return {"data": response, "error": None}
        except Exception as e:
            return {"data": None, "error": e}
