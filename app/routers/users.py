import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import create_jwt_token
from app.internal.supadb import SupabaseClient
from app.internal.users import User, UserQueries

router = APIRouter(
    prefix="/api/v1",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


def get_user_queries() -> UserQueries:
    return UserQueries(SupabaseClient())


ACCESS_TOKEN_EXPIRE_MINUTES = float(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15.0))


@router.post("/signup")
async def signup(user: User, user_queries: UserQueries = Depends(get_user_queries)):
    result = user_queries.register_user(user)
    if result["error"]:
        handle_error(result["error"], "error adding a user to the database")
    return {"data": "added user successfully"}


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/token")
async def login(
    login_request: LoginRequest, user_queries: UserQueries = Depends(get_user_queries)
):
    email = login_request.email
    password = login_request.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user_data = user_queries.get_user(email)
    if user_data["error"]:
        raise HTTPException(status_code=400, detail="Error fetching user by email")

    stored_password = user_data["data"].data[0]["password"]
    if not user_queries.verify_password(password, stored_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # create a new token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    try:
        access_token = create_jwt_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating JWT token: {str(e)}"
        )

    return {"access_token": access_token, "token_type": "bearer"}


def handle_error(error, error_message):
    if error:
        raise HTTPException(status_code=500, detail=f"{error_message}: {error}")
