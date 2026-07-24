from datetime import datetime

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.browse_history import BrowseHistory
from models.news import News


async def add_browse_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    """同一用户看同一新闻 → 更新浏览时间，不重复插入"""
    query = select(BrowseHistory).where(
        BrowseHistory.user_id == user_id,
        BrowseHistory.news_id == news_id
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.view_time = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        history = BrowseHistory(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    count_query = select(func.count()).where(BrowseHistory.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = (select(News, BrowseHistory.id.label("history_id"), BrowseHistory.view_time.label("view_time"))
             .join(BrowseHistory, BrowseHistory.news_id == News.id)
             .where(BrowseHistory.user_id == user_id)
             .order_by(BrowseHistory.view_time.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows, total


async def delete_browse_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    """按新闻ID删除（前端传的就是新闻ID）"""
    stmt = delete(BrowseHistory).where(
        BrowseHistory.news_id == news_id,
        BrowseHistory.user_id == user_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def clear_browse_history(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(BrowseHistory).where(BrowseHistory.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
