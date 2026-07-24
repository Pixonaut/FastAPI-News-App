import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security


async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRequest):
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) # add, commit之后，再从数据库拉最新数据更新到user对象
    return user


async def create_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(minutes=10)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
        # 已存在的对象将被session监听，如有修改，将在控制权回归get_db后统一commit
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None
    return user


async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token: UserToken | None = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_none=True,
        exclude_unset=True
    ))
    result = await db.execute(query)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 获取更新后的用户，前端用于更新页面
    updated_user = await get_user_by_username(db, username)
    return updated_user


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not security.verify_password(old_password, user.password):
        return False

    hashed_new_password = security.get_hash_password(new_password)
    user.password = hashed_new_password
    db.add(user) # 确保session接管状态，避免过期或关闭导致commit失败
    await db.commit()
    await db.refresh(user)
    return True
