import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password
from app.schemas.auth import SignupRequest


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    try:
        uid = uuid.UUID(str(user_id))
    except ValueError:
        return None
    result = await db.execute(select(User).where(User.id == uid))
    return result.scalar_one_or_none()


async def get_user_by_mobile(db: AsyncSession, mobile: str) -> User | None:
    result = await db.execute(select(User).where(User.mobile == mobile))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: SignupRequest) -> User:
    user = User(
        full_name=data.full_name.strip(),
        email=data.email.lower(),
        mobile=data.mobile,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()   # get the generated id without committing yet
    await db.refresh(user)
    return user


async def update_user_vua(db: AsyncSession, user_id: str, vua: str) -> User | None:
    user = await get_user_by_id(db, user_id)
    if user:
        user.vua = vua
        await db.flush()
        await db.refresh(user)
    return user
