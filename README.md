# nb_api

<p align="center">
  <!-- 你可以在这里放一个酷炫的 Logo -->
  <!-- <img src="path/to/your/logo.png" height="200" /> -->
</p>
<p align="center">
  <em>⚡️ 为你的数据模型闪电般地生成 CRUD API ⚡️</em>
</p>
<p align="center">
  <!-- 在这里可以添加一些徽章，比如 PyPI 版本、构建状态等 -->
  <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/nb_api">
  <img alt="License" src="https://img.shields.io/github/license/ydf0509/nb_api">
</p>

---

## 🚀 `nb_api` 是什么？

`nb_api` 是一个为现代 FastAPI 应用量身打造的 **CRUD 路由自动生成框架**。你只需定义好你的数据模型，`nb_api` 就能为你自动创建一整套完整、健壮且文档齐全的增、删、改、查（CRUD）API 接口。

`nb_api` 旨在解决为 FastAPI 应用重复编写 CRUD 接口的痛点。它支持多种数据存储后端，提供了更强大、更现代化的功能。

## ✨ 核心优势

- **多数据库支持**: 支持 **SQLModel**、**SQLAlchemy**、**Tortoise ORM** 和 **内存存储**，满足不同场景需求
- **现代化技术栈**: 完全基于 **FastAPI** + **Pydantic v2** 构建，享受最新的性能优化和最完善的类型提示
- **高度自动化**: 告别重复编写 CRUD 样板代码，让你专注于核心业务逻辑
- **强大的搜索能力**: 内置"超级搜索"接口，允许前端通过 JSON 动态构建复杂的过滤和排序查询
- **规范的 API 设计**: 所有响应都封装在统一的 `ResponseModel` 中，无论是成功还是失败，都有一致的结构，极大简化了前端处理
- **生产级特性**: 开箱即用的分页、依赖注入、慢请求日志记录等功能，让你的应用兼具开发效率和生产环境下的可观测性
- **灵活可扩展**: 轻松禁用、覆盖默认路由，或添加自定义路由，满足你的所有特殊需求

## 🛠️ 安装

```bash
pip install very_nb_api fastapi sqlmodel uvicorn
```

**注意安装和实际导入不同,因为提示nb_api这个名字和pypi已存在的包相似冲突了**
#### 安装
```
pip install very_nb_api
```

#### 导入
```
import nb_api
```

## 快速开始

### SQLModel 版本

在短短十几行代码内，即可拥有一个功能完备的 CRUD API。

```python
# main.py
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
from fastapi import FastAPI
from nb_api import SQLModelCRUDRouter

# 1. 定义 SQLModel 模型
class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str

# 2. 设置数据库
engine = create_engine("sqlite:///database.db")

def get_session():
    with Session(engine) as session:
        yield session

# 3. 创建 FastAPI 应用和 nb_api 路由
app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# 核心用法！
app.include_router(
    SQLModelCRUDRouter(schema=Book, db_model=Book, db_session=get_session)
)
```

### 异步 SQLModel 版本

```python
# main.py
from typing import Optional, AsyncGenerator
from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import FastAPI
from nb_api import AioSQLModelCRUDRouter

# 1. 定义 SQLModel 模型
class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str

# 2. 设置异步数据库
DATABASE_URL = "sqlite+aiosqlite:///database.db"
engine = create_async_engine(DATABASE_URL)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session

# 3. 创建 FastAPI 应用和 nb_api 路由
app = FastAPI()

# 核心用法！
app.include_router(
    AioSQLModelCRUDRouter(schema=Book, db_model=Book, db=get_session)
)
```

### Tortoise ORM 版本

```python
# main.py
from typing import Optional
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI
from pydantic import BaseModel
from nb_api import TortoiseCRUDRouter

# 1. 定义 Tortoise ORM 模型
class Book(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100)
    author = fields.CharField(max_length=100)

# 2. 定义 Pydantic 模型
class BookSchema(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        from_attributes = True

# 3. 创建 FastAPI 应用
app = FastAPI()

# 4. 注册 Tortoise ORM
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["__main__"]},
    generate_schemas=True,
    add_exception_handlers=True
)

# 核心用法！
app.include_router(
    TortoiseCRUDRouter(schema=BookSchema, db_model=Book, prefix="books")
)
```

### 内存版本（无需数据库）

```python
# main.py
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI
from nb_api import MemoryCRUDRouter

# 1. 定义 Pydantic 模型
class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str

# 2. 创建 FastAPI 应用
app = FastAPI()

# 核心用法！
app.include_router(
    MemoryCRUDRouter(schema=Book, prefix="books")
)
```

启动应用 `uvicorn main:app --reload`，然后访问 `http://127.0.0.1:8000/docs`，你将看到 `nb_api` 为 `Book` 模型自动生成的所有接口！

## 🌟 功能展示

### 1. 自动生成的 CRUD 路由

| 路由 | 方法 | 描述 |
|---|---|---|
| `/book` | `GET` | 获取所有书籍 (支持分页) |
| `/book` | `POST` | 创建一本新书 |
| `/book` | `DELETE` | 删除所有书籍 |
| `/book/{item_id}` | `GET` | 获取指定 ID 的书籍 |
| `/book/{item_id}` | `PUT` | 更新指定 ID 的书籍 |
| `/book/{item_id}` | `DELETE` | 删除指定 ID 的书籍 |
| `/book/search` | `POST` | **超级搜索接口** |

### 2. 超级搜索接口 (`/search`)

这是 `nb_api` 的独有功能！通过一个 `POST` 请求，实现复杂的动态查询。

**请求**: `POST /book/search`
**请求体**:
```json
{
  "filters": [
    { "field": "author", "operator": "contains", "value": "Tolkien" },
    { "field": "id", "operator": "in", "value": [1, 3, 5] }
  ],
  "sorting": [
    { "field": "title", "direction": "asc" }
  ]
}
```

### 3. 统一的 API 响应

**成功响应**:
```json
{
  "status_code": 0,
  "msg": "success",
  "data": { "id": 1, "title": "The Hobbit", "author": "J.R.R. Tolkien" }
}
```

**错误响应**:
```json
{
  "status_code": 404,
  "msg": "Item not found"
}
```

### 4. 路由定制与扩展

`nb_api` 提供了丰富的初始化参数来定制路由行为。

```python
from fastapi import Depends

router = SQLModelCRUDRouter(
    schema=Book,
    db_model=Book,
    db_session=get_session,
    
    # --- 功能配置 ---
    paginate=50,                  # 设置分页最大数量

    
    # --- 路由控制 ---
    prefix="my-books",            # 自定义路由前缀
    tags=["图书管理"],            # 自定义 OpenAPI 标签
    delete_all_route=False,       # 禁用"删除所有"路由
    
    # --- 依赖注入 (权限控制) ---
    update_route=[Depends(require_admin_user)],
    create_route=[Depends(require_login)]
)
```

你也可以像使用普通的 `APIRouter` 一样，轻松地覆盖或添加新路由。

```python
# 覆盖默认的 get_one 路由
@router.get("/{item_id}")
def custom_get_one(item_id: int):
    return {"message": f"You are viewing book {item_id} with a custom route!"}

# 添加一个全新的路由
@router.post("/{item_id}/publish")
def publish_book(item_id: int):
    # ... 发布逻辑 ...
    return {"message": "Book published!"}
```


### 5 一个接口没写,下面都是nb_api自动生成的接口

接口文档截图:
[![pVXA2ZD.png](https://s21.ax1x.com/2025/10/23/pVXA2ZD.png)](https://imgchr.com/i/pVXA2ZD)

这些接口都是nb_api自动生成的,你只需要定义好你的数据模型,nb_api就会自动生成这些接口,全部都不是人工手写def 的 fastapi 接口
