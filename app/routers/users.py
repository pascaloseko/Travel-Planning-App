import os
from datetime import timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uplink_python.errors import StorjException

from app.dependencies import create_jwt_token, decode_jwt_token, get_current_user
from app.internal.storj import StorjClient
from app.internal.supadb import SupabaseClient
from app.internal.users import User, UserQueries

router = APIRouter(
    prefix="/api/v1",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


def get_user_queries() -> UserQueries:
    return UserQueries(SupabaseClient())


def get_storj_client() -> StorjClient:
    return StorjClient()


ACCESS_TOKEN_EXPIRE_MINUTES = float(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15.0))


@router.post("/signup")
async def signup(user: User, user_queries: UserQueries = Depends(get_user_queries)):
    result = user_queries.register_user(user)
    if result["error"]:
        handle_error(result["error"], "error adding a user to the database")

    user_data = user_queries.get_user(user.email)
    if user_data["error"]:
        raise HTTPException(status_code=400, detail="Error fetching user by email")

    user_id = user_data["data"].data[0]["id"]
    username = user_data["data"].data[0]["username"]
    email = user_data["data"].data[0]["email"]
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

    return {"user_id": user_id, "username": username, "token": access_token}


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/token")
async def login(
    login_request: LoginRequest,
    user_queries: UserQueries = Depends(get_user_queries),
    storj_client: StorjClient = Depends(get_storj_client),
):
    email = login_request.email
    password = login_request.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user_data = user_queries.get_user(email)
    if user_data["error"]:
        raise HTTPException(status_code=400, detail="Error fetching user by email")

    user_id = user_data["data"].data[0]["id"]
    username = user_data["data"].data[0]["username"]
    stored_password = user_data["data"].data[0]["password"]
    if not user_queries.verify_password(password, stored_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        profile_data = await storj_client.get_user_profile_image()
    except StorjException as storj_error:
        raise HTTPException(
            status_code=400, detail=f"Error loading profile image: {storj_error}"
        )

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

    return JSONResponse(
        content={
            "user_id": user_id,
            "username": username,
            "token": access_token,
            "profile_image": profile_data,
        },
        status_code=200,
    )


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh-token")
async def refresh_token(
    rt: RefreshRequest, user_queries: UserQueries = Depends(get_user_queries)
):
    decoded_data = decode_jwt_token(rt.refresh_token)

    if decoded_data is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_data = user_queries.get_user(decoded_data["sub"])
    if user_data["error"]:
        raise HTTPException(status_code=400, detail="Error fetching user by email")

    user_id = user_data["data"].data[0]["id"]
    username = user_data["data"].data[0]["username"]

    # Create a new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"sub": decoded_data["sub"]}, expires_delta=access_token_expires
    )

    return {"user_id": user_id, "username": username, "token": access_token}


@router.post("/protected/upload-profile")
async def upload_profile_image(
    profile_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    user_queries: UserQueries = Depends(get_user_queries),
    storj_client: StorjClient = Depends(get_storj_client),
):
    try:
        file_content = await profile_image.read()

        user_info = user_queries.get_user(current_user.get("sub"))
        if not user_info:
            return JSONResponse(
                status_code=400, content={"detail": "Error fetching user by email"}
            )

        user_id = user_info["data"].data[0]["id"]
        uploaded = await storj_client.upload_user_profile(
            user_id, profile_image.filename, file_content
        )
        if uploaded != "":
            return JSONResponse(status_code=500, content={"detail": f"{uploaded}"})
        return {"data": "image uploaded succesfully"}
    except Exception as e:
        return JSONResponse(content={"detail": str(e)}, status_code=500)


def handle_error(error, error_message):
    if error:
        raise HTTPException(status_code=500, detail=f"{error_message}: {error}")
