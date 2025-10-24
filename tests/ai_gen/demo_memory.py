"""内存 CRUD Router 示例"""

from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

from nb_api import MemoryCRUDRouter

# 定义 Pydantic 模型
class Book(BaseModel):
    """图书模型"""
    id: Optional[int] = None
    title: str
    author: str
    price: float
    isbn: str

    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    """图书创建模型"""
    title: str
    author: str
    price: float
    isbn: str


class BookUpdate(BaseModel):
    """图书更新模型"""
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    isbn: Optional[str] = None


# 创建 FastAPI 应用
app = FastAPI(
    title="内存 CRUD 示例",
    root_path="/test_nb_api",
    redirect_slashes=False
)


# 创建 CRUD 路由
book_router = MemoryCRUDRouter(
    schema=Book,
    create_schema=BookCreate,
    update_schema=BookUpdate,
    prefix="books",
    tags=["图书管理"],
    paginate=20  # 每页最多20条
)

# 注册路由
app.include_router(book_router)


# 预先添加10条测试数据
@app.on_event("startup")
async def add_initial_data():
    """添加初始测试数据"""
    from nb_api.core.mem import _memory_stores, _id_counters
    
    # 获取 books 存储
    books_store = _memory_stores.get("books", [])
    
    # 添加10条测试数据
    test_books = [
        {"title": "Python编程入门", "author": "张三", "price": 59.0, "isbn": "978-001"},
        {"title": "数据结构与算法", "author": "李四", "price": 79.0, "isbn": "978-002"},
        {"title": "机器学习实战", "author": "王五", "price": 89.0, "isbn": "978-003"},
        {"title": "深度学习原理", "author": "赵六", "price": 99.0, "isbn": "978-004"},
        {"title": "Web开发指南", "author": "钱七", "price": 69.0, "isbn": "978-005"},
        {"title": "数据库系统概念", "author": "孙八", "price": 75.0, "isbn": "978-006"},
        {"title": "操作系统原理", "author": "周九", "price": 85.0, "isbn": "978-007"},
        {"title": "计算机网络", "author": "吴十", "price": 65.0, "isbn": "978-008"},
        {"title": "软件工程实践", "author": "郑一", "price": 95.0, "isbn": "978-009"},
        {"title": "人工智能导论", "author": "王二", "price": 109.0, "isbn": "978-010"}
    ]
    
    # 添加到存储中
    for i, book_data in enumerate(test_books, 1):
        book_data["id"] = i
        books_store.append(Book(**book_data))
    
    # 更新 ID 计数器
    _id_counters["books"] = 11
    
    print(f"已添加 {len(books_store)} 条初始数据")


@app.get("/")
async def root():
    return {"message": "内存 CRUD API 正常运行"}


if __name__ == "__main__":
    print("启动服务器...")
    print("API 文档: http://127.0.0.1:8011/docs")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8011,
        reload=False,
        log_level="info"
    )