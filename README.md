# nb_api

<p align="center">
  <!-- 你可以在这里放一个酷炫的 Logo -->
  <!-- <img src="path/to/your/logo.png" height="200" /> -->
</p>
<p align="center">
  <em>⚡️ 为你的 SQLModel 模型闪电般地生成 CRUD API ⚡️</em>
</p>
<p align="center">
  <!-- 在这里可以添加一些徽章，比如 PyPI 版本、构建状态等 -->
  <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/nb_api">
  <img alt="License" src="https://img.shields.io/github/license/ydf0509/nb_api">
</p>

---

## 🚀 `nb_api` 是什么？

`nb_api` 是一个为现代 FastAPI 应用量身打造的 **CRUD 路由自动生成框架**。你只需定义好你的 `SQLModel` 模型，`nb_api` 就能为你自动创建一整套完整、健壮且文档齐全的增、删、改、查（CRUD）API 接口。

它的诞生是为了解决 `fastapi-crudrouter` 停止维护且不兼容 Pydantic v2 的问题，并在此基础上提供了更强大、更现代化的功能。

## ✨ 核心优势

- **现代化技术栈**: 完全基于 **FastAPI** + **Pydantic v2** + **SQLModel** 构建，享受最新的性能优化和最完善的类型提示。
- **高度自动化**: 告别重复编写 CRUD 样板代码，让你专注于核心业务逻辑。
- **强大的搜索能力**: 内置“超级搜索”接口，允许前端通过 JSON 动态构建复杂的过滤和排序查询。
- **规范的 API 设计**: 所有响应都封装在统一的 `ResponseModel` 中，无论是成功还是失败，都有一致的结构，极大简化了前端处理。
- **生产级特性**: 开箱即用的分页、依赖注入、慢请求日志记录等功能，让你的应用兼具开发效率和生产环境下的可观测性。
- **灵活可扩展**: 轻松禁用、覆盖默认路由，或添加自定义路由，满足你的所有特殊需求。

## 🛠️ 安装

```bash
pip install nb_api fastapi sqlmodel uvicorn
```

## 快速开始

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
    delete_all_route=False,       # 禁用“删除所有”路由
    
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

## 💡 与 `fastapi-crudrouter` 的关系

`nb_api` 旨在成为 `fastapi-crudrouter` 在现代 Python & FastAPI 生态中的精神继承者和功能升级版。它解决了 `fastapi-crudrouter` 因停止维护而带来的兼容性问题，并专注于 `SQLModel`，提供了更强大、更易用的功能。

## 许可证

本项目采用 MIT 许可证。

