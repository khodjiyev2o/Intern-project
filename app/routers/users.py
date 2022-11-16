from schemas.users import UserCreateSchema, UserLoginSchema, UserSchema, UserAlterSchema
from models.users import User
from services.users import UserCRUD, get_user, get_or_create_user
from db import get_session
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

user_router = APIRouter()


@user_router.get('/users/validate', response_model=UserSchema)
async def validate(user: UserSchema = Depends(get_or_create_user)) -> UserSchema:
    return user


@user_router.get('/users', response_model=list[UserSchema])
async def users(session: AsyncSession = Depends(get_session), page: int = Query(default=1)) -> list[UserSchema]:
    result = await UserCRUD(session=session).get_users(page)
    return result


@user_router.get('/users/{id}', response_model=UserSchema)
async def user(id: int, session: AsyncSession = Depends(get_session)) -> UserSchema:
    user = await UserCRUD(session=session).get_user(id)
    return user


@user_router.post('/users', response_model=UserSchema)
async def add_user(user: UserCreateSchema, session: AsyncSession = Depends(get_session)) -> UserSchema:
    user = await UserCRUD(session=session).create_user(user)
    return user


@user_router.post('/users/login', response_model=str)
async def log_user(user: UserLoginSchema, session: AsyncSession = Depends(get_session)) -> str:
    token = await UserCRUD(session=session).login_user(user)
    return token


@user_router.patch('/users', response_model=UserSchema)
async def patch_user(user: UserAlterSchema, db_user: User = Depends(get_user)) -> UserSchema:
    user = await UserCRUD(user=db_user).patch_user(user)
    return user


@user_router.delete('/users', response_model=UserSchema)
async def delete_user(user: User = Depends(get_user)) -> UserSchema:
    user = await UserCRUD(user=user).delete_user()
    return user
