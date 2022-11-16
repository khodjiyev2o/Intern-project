from services.services import create_token, read_token
from models.users import User
from sqlalchemy.future import select
from sqlalchemy import or_
from fastapi import HTTPException, Header, Depends
from schemas.users import UserAlterSchema, UserCreateSchema, UserLoginSchema, UserSchema
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.ext.asyncio import AsyncSession, async_object_session
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_pagination import Params
from db import get_session
from os import getenv
from typing import Optional


class UserCRUD:
    def __init__(self, session: Optional[AsyncSession] = None, user: Optional[User] = None):
        if not session:
            self.session = async_object_session(user)
        else:
            self.session = session
        self.user = user

    async def create_user(self, user: UserCreateSchema) -> UserSchema:
        db_user = await self.session.execute(select(User).filter(or_(User.email == user.email, User.username == user.username)))
        db_user = db_user.scalars().first()
        if db_user:
            raise HTTPException(404, 'username or email already in use')
        else:
            new_user = User(username=user.username, email=user.email, password=sha256.hash(user.password1), description=user.description)
            self.session.add(new_user)
            await self.session.commit()
            return UserSchema(id=new_user.id, username=new_user.username, email=new_user.email, description=new_user.description)

    async def login_user(self, user: UserLoginSchema) -> str:
        db_user = await self.session.execute(select(User).filter_by(email=user.email))
        db_user = db_user.scalars().first()
        if db_user:
            if sha256.verify(user.password, db_user.password):
                return create_token({'email': user.email})
            else:
                raise HTTPException(404, 'user not found')
        else:
            raise HTTPException(404, 'user not found')

    async def patch_user(self, user: UserAlterSchema) -> UserSchema:
        if user.username:
            self.user.username = user.username
        if user.description:
            self.user.description = user.description
        if user.password:
            self.user.password = sha256.hash(user.password)
        await self.session.commit()
        return UserSchema(id=self.user.id, username=self.user.username, email=self.user.email, description=self.user.description)

    async def get_users(self, page: int) -> list[UserSchema]:
        params = Params(page=page, size=10)
        users = await paginate(self.session, select(User), params=params)
        return [UserSchema(id=user.id, username=user.username, email=user.email, description=user.description) for user in users.items]

    async def get_user(self, id: int) -> UserSchema:
        user = await self.session.get(User, id)
        if user:
            return UserSchema(id=user.id, username=user.username, email=user.email, description=user.description)
        raise HTTPException(404, 'user not found')

    async def delete_user(self) -> UserSchema:
        return_user = UserSchema(id=self.user.id, username=self.user.username, email=self.user.email, description=self.user.description)
        await self.session.delete(self.user)
        await self.session.commit()
        return return_user


async def get_or_create_user(session: AsyncSession = Depends(get_session), Token: str = Header(), TokenType: str = Header()) -> User:
    email = read_token(Token, TokenType)
    user = await session.execute(select(User).filter(User.email == email))
    user = user.scalars().first()

    if user:
        return UserSchema(id=user.id, username=user.username, email=user.email, description=user.description)
    else:
        if TokenType == 'app':
            raise HTTPException(404, 'user validation error')
        elif TokenType == 'auth0':
            new_user = User(username=email, email=email, password=sha256.hash(getenv('SECRET_KEY')))
            session.add(new_user)
            await session.commit()
            return UserSchema(id=new_user.id, username=new_user.username, email=new_user.email, description=new_user.description)


async def get_user(session: AsyncSession = Depends(get_session), Token: str = Header(), TokenType: str = Header()) -> User:
    email = read_token(Token, TokenType)
    user = await session.execute(select(User).filter(User.email == email))
    user = user.scalars().first()
    if user:
        return user
    else:
        raise HTTPException(404, 'user validation error')
