import motor.motor_asyncio
from bson import ObjectId
from fastapi import HTTPException

from darqube_test.app.config import settings
from darqube_test.app.serializers import serialize_user

client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL)

database = client[settings.MONGO_DB]

user_collection = database.get_collection("users")

SENTINEL = object()


async def check_unique_email(value):
    if await user_collection.find_one({"email": value}):
        return False
    return True


# Get users
async def retrieve_users():
    users = []
    async for user in user_collection.find():
        users.append(serialize_user(user))
    return users


# New user
async def add_user(data: dict) -> dict:
    from darqube_test.app.encryption import encrypt_password
    data["hashed_pass"] = encrypt_password(data["hashed_pass"])
    if not await check_unique_email(data["email"]):
        raise HTTPException(status_code=422, detail="User with such email already exists!")
    user = await user_collection.insert_one(data)
    return {"id": str(user.inserted_id)}


# Retrieve by ID
async def retrieve_user(id: str) -> dict:
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        return serialize_user(user)


# Update by ID
async def update_user(id: str, data: dict):
    if len(data) < 1:
        return False
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        updated = await user_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated:
            return True
        return False


async def delete_user(id: str):
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        await user_collection.delete_one({"_id": ObjectId(id)})
        return True


async def get_user(email, default=SENTINEL):
    user = await user_collection.find_one({"email": email})
    if not user:
        if default is not SENTINEL:
            return default
        raise LookupError(email)
    return user
