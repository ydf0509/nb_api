"""内存 CRUD Router 示例"""

from pydantic import BaseModel
from fastapi import FastAPI
from nb_api import MemoryCRUDRouter


class Potato(BaseModel):
    """土豆模型"""
    id: int
    color: str
    mass: float
    thickness: float


# 创建 FastAPI 应用
app = FastAPI(title="Memory CRUD 示例")

# 创建 CRUD 路由
router = MemoryCRUDRouter(
    schema=Potato,
    prefix="potatoes",
    tags=["土豆管理"],
    paginate=10  # 每页最多10条
)

# 注册路由
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    
    print("启动服务器...")
    print("API 文档: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)

