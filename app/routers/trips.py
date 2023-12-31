import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.dependencies import get_current_user
from app.internal.supadb import SupabaseClient
from app.internal.trips import Trip, TripQueries
from app.internal.users import UserQueries

router = APIRouter(
    prefix="/api/v1",
    tags=["trips"],
    responses={404: {"description": "Not found"}},
)


class QueryDependencies:
    def __init__(self, trip_queries: TripQueries, user_queries: UserQueries):
        self.trip_queries = trip_queries
        self.user_queries = user_queries


def get_queries() -> QueryDependencies:
    supabase_client = SupabaseClient()
    return QueryDependencies(TripQueries(supabase_client), UserQueries(supabase_client))


@router.post("/protected/trips")
async def create_trip(
    request: Request,
    queries: QueryDependencies = Depends(get_queries),
    current_user: dict = Depends(get_current_user),
):
    try:
        request_body = await request.body()
        request_data = request_body.decode("utf-8")

        # Parse the JSON string into a dictionary
        trip_data = json.loads(request_data)

        # Validate the Trip model
        validated_trip = Trip.model_validate(trip_data)

        user_info = queries.user_queries.get_user(current_user.get("sub"))
        if not user_info:
            raise HTTPException(status_code=400, detail="Error fetching user by email")

        user_id = user_info["data"].data[0]["id"]
        result = queries.trip_queries.create_trip(validated_trip, user_id)
        if result["error"]:
            handle_error(result["error"], "error creating trip")

        trip_id = result["data"][1][0]["id"]
        return {"trip_id": trip_id, "message": "Trip created successfully"}
    except ValidationError as e:
        return JSONResponse(content={"detail": str(e)}, status_code=400)


@router.get("/protected/trips")
async def get_user_trips(
    queries: QueryDependencies = Depends(get_queries),
    current_user: dict = Depends(get_current_user),
):
    user_info = queries.user_queries.get_user(current_user.get("sub"))
    if not user_info:
        raise HTTPException(status_code=400, detail="Error fetching user by email")

    user_id = user_info["data"].data[0]["id"]
    result = queries.trip_queries.get_user_trips(user_id)
    if result["error"]:
        handle_error(result["error"], "error fetching user trips")
    return result["data"]


def handle_error(error, error_message):
    if error:
        raise HTTPException(status_code=500, detail=f"{error_message}: {error}")
