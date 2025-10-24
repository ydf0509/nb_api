"""SQLAlchemy CRUD Router 示例"""

from typing import Optional, Generator
from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine
from sqlalchemy.orm import Session, declarative_base
from fastapi import FastAPI
from nb_api import SQLAlchemyCRUDRouter
from nb_log import get_logger
from pydantic import BaseModel

logger = get_logger("name1")
get_logger("uvicorn")

# 创建基类
Base = declarative_base()

# 定义 SQLAlchemy 模型
class BookModel(Base):
    """图书 SQLAlchemy 模型"""
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    price = Column(Float)
    isbn = Column(String, unique=True)


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


# 创建数据库引擎
DATABASE_URL = "sqlite:///./test_sqlalchemy.db"
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """初始化数据库"""
    logger.info("初始化数据库")
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """获取数据库会话"""
    with Session(engine) as session:
        yield session


# 创建 FastAPI 应用
app = FastAPI(title="SQLAlchemy CRUD 示例", root_path="/test_nb_api")


# 初始化数据库
@app.on_event("startup")
def on_startup():
    init_db()


# 创建 CRUD 路由
book_router = SQLAlchemyCRUDRouter(
    schema=BookSchema,
    create_schema=BookCreateSchema,
    update_schema=BookUpdateSchema,
    db_model=BookModel,
    db=get_session,
    prefix="books",
    tags=["图书管理"],
    paginate=20,  # 每页最多20条
)

# 注册路由
app.include_router(book_router)


if __name__ == "__main__":
    import uvicorn
    
    print("启动服务器...")
    print("API 文档: http://127.0.0.1:8003/docs")
    # 使用 reload=False 避免 SQLAlchemy 表重复定义错误
    uvicorn.run(app, host="127.0.0.1", port=8003, reload=False,
                log_config={"version": 1}
    )
    """
    uvicorn tests.ai_gen.demo_sqlalchemy:app --host 127.0.0.1 --port 8003 --reload

    uvicorn tests.ai_gen.demo_sqlalchemy:app --host 0.0.0.0 --port 8004 --workers 2
    """