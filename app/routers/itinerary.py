from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.internal.itinerary import Itinerary, ItineraryQueries
from app.internal.supadb import SupabaseClient

router = APIRouter(
    prefix="/api/v1",
    tags=["itinerary"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)


def get_itinerary_queries() -> ItineraryQueries:
    return ItineraryQueries(SupabaseClient())


@router.post("/protected/{trip_id}/itinerary")
async def create_itinerary(
    it: Itinerary,
    trip_id,
    it_queries: ItineraryQueries = Depends(get_itinerary_queries),
):
    result = it_queries.create_itinerary(it, trip_id)
    if result["error"]:
        handle_error(result["error"], "error creating itinerary")
    it_id = result["data"][1][0]["id"]
    return {"itinerary_id": it_id, "message": "Trip created successfully"}


@router.get("/protected/{trip_id}/itinerary")
async def get_trip_itineraries(
    trip_id, it_queries: ItineraryQueries = Depends(get_itinerary_queries)
):
    result = it_queries.get_trip_itineraries(trip_id)
    if result["error"]:
        handle_error(result["error"], "error getting itinerary")
    return result["data"]


def handle_error(error, error_message):
    if error:
        raise HTTPException(status_code=500, detail=f"{error_message}: {error}")
