"""异步 SQLModel CRUD Router 示例"""

from typing import AsyncGenerator, Optional
from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager

from nb_api import AioSQLModelCRUDRouter

# 定义 SQLModel 模型
class Book(SQLModel, table=True):
    """图书模型"""
    __tablename__ = "books"
    __table_args__ = {'extend_existing': True}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str
    price: float
    isbn: str = Field(unique=True)


# 定义 Pydantic Schema (用于 API 响应)
class BookSchema(BaseModel):
    """图书基础模型"""
    id: int
    title: str
    author: str
    price: float
    isbn: str

    class Config:
        from_attributes = True


class BookCreateSchema(BaseModel):
    """图书创建模型"""
    title: str
    author: str
    price: float
    isbn: str


class BookUpdateSchema(BaseModel):
    """图书更新模型"""
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    isbn: Optional[str] = None


# 创建异步数据库引擎
DATABASE_URL = "sqlite+aiosqlite:///./test_aio_sqlmodel.db"
engine = create_async_engine(DATABASE_URL, echo=True)


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSession(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    await init_db()
    yield

# 创建 FastAPI 应用
app = FastAPI(
    title="异步 SQLModel CRUD 示例",
    root_path="/test_nb_api",
    redirect_slashes=False,
    lifespan=lifespan
)


# 初始化数据库已移至 lifespan


# 创建 CRUD 路由
book_router = AioSQLModelCRUDRouter(
    schema=BookSchema,
    create_schema=BookCreateSchema,
    update_schema=BookUpdateSchema,
    db_model=Book,
    db=get_session,
    prefix="books",
    tags=["图书管理"],
    paginate=20,  # 每页最多20条
)

# 注册路由
app.include_router(book_router)


@app.get("/")
async def root():
    return {"message": "异步 SQLModel CRUD API 正常运行"}


if __name__ == "__main__":
    print("启动服务器...")
    print("API 文档: http://127.0.0.1:8010/docs")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8010,
        reload=False,
        log_level="info"
    )