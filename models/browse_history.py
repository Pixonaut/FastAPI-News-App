from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from models.news import News
from models.users import User


class Base(DeclarativeBase):
    pass


class BrowseHistory(Base):
    """
    浏览历史表 ORM 模型
    """
    __tablename__ = "history"
    # 创建索引 + 唯一约束（同一用户对同一新闻只存一条）
    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uq_user_news_history"),
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="浏览记录ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False, comment="新闻ID")
    view_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, comment="浏览时间")

    def __repr__(self):
        return f"<BrowseHistory(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, view_time={self.view_time})>"
