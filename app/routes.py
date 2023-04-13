from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from darqube_test.app.db import (
    add_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user, get_user,
)
from darqube_test.app.encryption import verify_password, create_access_token, create_refresh_token, get_current_user, requires_role
from darqube_test.app.models import UserSchema, UpdateUserSchema, JWTResponseSchema, CreateUserSchema

router = APIRouter()


@router.post("/create_user/", response_description="User data added.")
async def add_new_user(user: CreateUserSchema):
    user = jsonable_encoder(user)
    new = await add_user(user)
    return new


@router.get("/get_users/", response_description="Users retrieved.")
async def get_users():
    users = await retrieve_users()
    if users:
        return users


@router.get("/get_user/{id}", response_description="User data retrieved.")
async def get_user_data(id):
    try:
        user = await retrieve_user(id)
    except InvalidId:
        raise HTTPException(status_code=422, detail="Invalid user ID.")
    return user


@router.put("/update_user/{id}")
async def update_user_data(
        id: str, req: UpdateUserSchema,
        user: UserSchema = Depends(requires_role("admin"))
):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = await update_user(id, req)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not find",
        )
    return "User updated", status.HTTP_204_NO_CONTENT


@router.delete("/delete_user/{id}", response_description="User deleted.")
async def delete_user_data(id: str):
    deleted_user = await delete_user(id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not find",
        )
    return "User updated", status.HTTP_204_NO_CONTENT


@router.post('/login', summary="Create access and refresh tokens for user", response_model=JWTResponseSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username, None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['hashed_pass']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    }


@router.get('/me', summary='Get details of currently logged in user', response_model=UserSchema)
async def get_me(user: UserSchema = Depends(get_current_user)):
    return user
