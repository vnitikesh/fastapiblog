from fastapi import FastAPI, Depends
from .database import engine, Base, async_session_maker
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.db import SQLAlchemyUserDatabase
from api_models import UserTable
from fastapi_users import UUIDIDMixin, BaseUserManager, InvalidPasswordException
import uuid
from typing import Optional, Union


app = FastAPI()

# Utility function to create defined tables in api_models
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Database Adapter Dependency(Link between db config and Users logic)

# Returns fresh sqlalchemy session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

#Generate adapter using above session
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, UserTable)

SECRET = "secret"

class UserManager(UUIDIDMixin, BaseUserManager[UserTable, uuid.UUID]):
    reset_password_token_secret = SECRET # Secret to encode reset password token
    verification_token_secret = SECRET # Secret to encode verification token

    async def validate_password(self, password: str, user: UserTable) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(reason= "Password should be atleast 8 characters")
        if user.email in password:
            raise InvalidPasswordException(reason= "Password should not contain email")



    async def on_after_register(self, user: UserTable, request: Optional[Request] = None):
        # Send welcome email or add it to analytics pipeline
        print(f"User {user.id} has registered")

    async def on_after_forgot_password(self, user: UserTable, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password, Reset token: {token}")

    async def on_after_request_verify(self, user: UserTable, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        

async def get_user_manager(user_db = Depends(get_user_db)):
    yield UserManager(user_db)
