"""Tortoise ORM CRUD Router 示例"""

from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
import uvicorn

from nb_api.core.tortoise import TortoiseCRUDRouter

# 定义 Tortoise ORM 模型
class BookModel(Model):
    """图书 Tortoise ORM 模型"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100, index=True)
    author = fields.CharField(max_length=100)
    price = fields.FloatField()
    isbn = fields.CharField(max_length=20, unique=True)

    class Meta:
        table = "books"

    def __str__(self):
        return self.title


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


# 创建 FastAPI 应用
app = FastAPI(
    title="Tortoise ORM CRUD 示例",
    root_path="/test_nb_api",
    redirect_slashes=False
)


# 注册 Tortoise ORM
register_tortoise(
    app,
    db_url="sqlite://./test_tortoise.db",
    modules={"models": ["tests.ai_gen.demo_tortoise"]},
    generate_schemas=True,
    add_exception_handlers=True
)


# 创建 CRUD 路由
book_router = TortoiseCRUDRouter(
    schema=BookSchema,
    create_schema=BookCreateSchema,
    update_schema=BookUpdateSchema,
    db_model=BookModel,
    prefix="books",
    tags=["图书管理"],
    paginate=20,  # 每页最多20条
)

# 注册路由
app.include_router(book_router)


@app.get("/")
async def root():
    return {"message": "Tortoise ORM CRUD API 正常运行"}


if __name__ == "__main__":
    print("启动服务器...")
    print("API 文档: http://127.0.0.1:8008/docs")
    uvicorn.run(
        "tests.ai_gen.demo_tortoise:app",
        host="127.0.0.1",
        port=8008,
        reload=False,
        log_level="info"
    )