from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from models.users import User
from schemas.browse_history import HistoryAddRequest, HistoryAddResponse, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import browse_history

router = APIRouter(prefix="/api/history", tags=["browse_history"])


@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await browse_history.add_browse_history(db, user.id, data.news_id)
    return success_response(message="添加成功", data=HistoryAddResponse.model_validate(result))


@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows, total = await browse_history.get_history_list(db, user.id, page, page_size)
    history_list = [{
        **news.__dict__,
        "history_id": history_id,
        "view_time": view_time,
    } for news, history_id, view_time in rows]
    has_more = total > page * page_size

    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取浏览历史成功", data=data)


@router.delete("/delete/{news_id}")
async def delete_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await browse_history.delete_browse_history(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="浏览记录不存在")
    return success_response(message="删除成功")


@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await browse_history.clear_browse_history(db, user.id)
    return success_response(message=f"清空了{count}条浏览历史")
