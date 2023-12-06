import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

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
    request: Request,
    trip_id,
    it_queries: ItineraryQueries = Depends(get_itinerary_queries),
):
    try:
        request_body = await request.body()
        request_data = request_body.decode("utf-8")

        itinerary_data = json.loads(request_data)

        validated_itinerary = Itinerary.model_validate(itinerary_data)

        result = it_queries.create_itinerary(validated_itinerary, trip_id)
        if result["error"]:
            handle_error(result["error"], "error creating itinerary")
        it_id = result["data"][1][0]["id"]
        return {"itinerary_id": it_id, "message": "Trip created successfully"}
    except ValidationError as e:
        return JSONResponse(content={"detail": str(e)}, status_code=400)


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
