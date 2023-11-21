import os
from datetime import timedelta

from fastapi import FastAPI, HTTPException

from app.dependencies import create_jwt_token
from app.internal.supadb import SupabaseClient
from app.internal.users import UserQueries, User

app = FastAPI()
user_queries = UserQueries(SupabaseClient())

ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")


@app.post("/signup")
async def signup(user: User):
    if user.username in user_queries.get_users():
        raise HTTPException(status_code=400, detail="Username already registered")

    result = user_queries.register_user(user)
    if result["error"]:
        handle_error(result["error"], "error adding a user to the database")


@app.post("/token")
async def login(email: str, password: str):
    user = user_queries.get_user(email)
    if user["error"]:
        raise HTTPException(status_code=400, detail="error fetching user by name")

    if not user_queries.verify_password(password, user["result"]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # create a new token
    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_jwt_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def handle_error(error, error_message):
    if error:
        raise HTTPException(status_code=500, detail=f"{error_message}: {error}")
