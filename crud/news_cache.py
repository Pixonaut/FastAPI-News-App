from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import get_cache_categories, set_cache_categories, get_cache_news_list, set_cache_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    cached_categories = await get_cache_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories =  result.scalars().all()

    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)

    return categories


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100):
    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)
    if cached_list:
        return [News(**item) for item in cached_list]

    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list =  result.scalars().all()

    if news_list:
        # by_alias=False 因为写入Redis的数据是给后端用的
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list


async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 更新：检查数据库是否命中数据 -> 返回命中结果
    return result.rowcount > 0

# 获取同类新闻（不含自身），浏览量、发布时间降序，5条
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in related_news]