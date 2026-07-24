from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"


async def get_cache_categories():
    return await get_json_cache(CATEGORIES_KEY)


async def set_cache_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)


async def set_cache_news_list(
        category_id: Optional[int],
        page: int,
        size: int,
        news_list: List[Dict[str, Any]],
        expire: int = 1800
):
    category_part = category_id if category_id else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key, news_list, expire)


async def get_cache_news_list(
        category_id: Optional[int],
        page: int,
        size: int
):
    category_part = category_id if category_id else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)