"""SQLModel CRUD Router 示例"""

from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
from fastapi import FastAPI
from nb_api import SQLModelCRUDRouter
from nb_log import get_logger

logger = get_logger("name1")
get_logger("uvicorn")

# 定义 SQLModel 模型
class Book(SQLModel, table=True):
    """图书模型"""
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str
    price: float
    isbn: str = Field(unique=True)


# 定义 Pydantic Schema (用于 API 响应)
class BookRead(SQLModel):
    """图书读取模型"""
    id: int
    title: str
    author: str
    price: float
    isbn: str


class BookCreate(SQLModel):
    """图书创建模型"""
    title: str
    author: str
    price: float
    isbn: str


class BookUpdate(SQLModel):
    """图书更新模型"""
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    isbn: Optional[str] = None


# 创建数据库引擎
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """初始化数据库"""
    logger.info("初始化数据库")
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session


# 创建 FastAPI 应用
app = FastAPI(title="SQLModel CRUD 示例",root_path="/test_nb_api")


# 初始化数据库
@app.on_event("startup")
def on_startup():
    
    init_db()


# 创建 CRUD 路由
book_router = SQLModelCRUDRouter(
    schema=BookRead,
    create_schema=BookCreate,
    update_schema=BookUpdate,
    db_model=Book,
    db=get_session,
    prefix="books",
    tags=["图书管理"],
    paginate=20,  # 每页最多20条,
   
)

# 注册路由
app.include_router(book_router)


if __name__ == "__main__":
    import uvicorn
    
    print("启动服务器...")
    print("API 文档: http://127.0.0.1:8001/docs")
    # 使用 reload=False 避免 SQLModel 表重复定义错误
    # uvicorn.run('demo_sqlmodel:app', host="127.0.0.1", port=8001, reload=False)
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False,
                log_config={"version": 1}
    )
    """
    uvicorn tests.ai_gen.demo_sqlmodel:app --host 127.0.0.1 --port 8002 --reload

    uvicorn tests.ai_gen.demo_sqlmodel:app --host 0.0.0.0 --port 8003 --workers 2
    """

