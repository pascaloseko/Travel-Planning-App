from datetime import datetime
from app.internal.supadb import SupabaseClient
from pydantic import BaseModel


class Itinerary(BaseModel):
    date: str
    description: str
    location: str
    activity: str


class ItineraryQueries:
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client

    def create_itinerary(self, itinerary: Itinerary, trip_id: int) -> dict:
        try:
            date = datetime.strptime(itinerary.date, "%Y-%m-%d").date()

            data, count = (
                self.supabase_client.client.table("itinerary")
                .insert(
                    [
                        {
                            "trip_id": trip_id,
                            "date": date.isoformat(),
                            "description": itinerary.description,
                            "location": itinerary.location,
                            "activity": itinerary.activity,
                        }
                    ]
                )
                .execute()
            )

            return {"data": data, "error": None}
        except Exception as e:
            return {"data": None, "error": str(e)}

    def get_trip_itineraries(self, trip_id: int):
        try:
            response = (
                self.supabase_client.client.table("itinerary")
                .select("*")
                .eq("trip_id", trip_id)
                .execute()
            )
            return {"data": response, "error": None}
        except Exception as e:
            return {"data": None, "error": e}
