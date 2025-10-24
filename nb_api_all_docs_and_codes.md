# markdown content namespace: nb_api readme 


## File Tree


```

└── README.md

```

---


## Included Files


- `README.md`


---


### code file start: README.md 

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

`nb_api` 旨在解决为 FastAPI 应用重复编写 CRUD 接口的痛点。它吸取了现有工具的优点，并针对 Pydantic v2 和 SQLModel 进行了深度优化，提供了更强大、更现代化的功能。

## ✨ 核心优势

- **现代化技术栈**: 完全基于 **FastAPI** + **Pydantic v2** + **SQLModel** 构建，享受最新的性能优化和最完善的类型提示。
- **高度自动化**: 告别重复编写 CRUD 样板代码，让你专注于核心业务逻辑。
- **强大的搜索能力**: 内置“超级搜索”接口，允许前端通过 JSON 动态构建复杂的过滤和排序查询。
- **规范的 API 设计**: 所有响应都封装在统一的 `ResponseModel` 中，无论是成功还是失败，都有一致的结构，极大简化了前端处理。
- **生产级特性**: 开箱即用的分页、依赖注入、慢请求日志记录等功能，让你的应用兼具开发效率和生产环境下的可观测性。
- **灵活可扩展**: 轻松禁用、覆盖默认路由，或添加自定义路由，满足你的所有特殊需求。

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


### 5 一个接口没写,下面都是nb_api自动生成的接口

接口文档截图:
[![pVXA2ZD.png](https://s21.ax1x.com/2025/10/23/pVXA2ZD.png)](https://imgchr.com/i/pVXA2ZD)

这些接口都是nb_api自动生成的,你只需要定义好你的SQLModel模型,nb_api就会自动生成这些接口,全部都不是人工手写def 的 fastapi 接口


**code file end: README.md**

---

# markdown content namespace: nb_api codes 


## File Tree


```

└── nb_api
    ├── __init__.py
    ├── contrib
    │   └── fastapi_helpers.py
    └── core
        ├── __init__.py
        ├── base.py
        ├── mem.py
        ├── sqlmodel.py
        ├── types.py
        └── utils.py

```

---


## Included Files


- `nb_api/__init__.py`

- `nb_api/contrib/fastapi_helpers.py`

- `nb_api/core/base.py`

- `nb_api/core/mem.py`

- `nb_api/core/sqlmodel.py`

- `nb_api/core/types.py`

- `nb_api/core/utils.py`

- `nb_api/core/__init__.py`


---


### code file start: nb_api/__init__.py 

```python
"""nb_api - 基于 FastAPI + Pydantic v2 + SQLModel 的自动 CRUD 路由生成框架"""

# from .core import (
#     CRUDGenerator,
#     SQLModelCRUDRouter,
#     MemoryCRUDRouter,
# )


from .core.base import CRUDGenerator
from .core.sqlmodel import SQLModelCRUDRouter



```

**code file end: nb_api/__init__.py**

---


### code file start: nb_api/contrib/fastapi_helpers.py 

```python

# slow_logger.py
import time
import logging
from typing import Optional, List
from fastapi import FastAPI, Request
from fastapi.responses import Response

def add_slow_request_logger(
    app: FastAPI,
    logger: logging.Logger,
    *,
    threshold: float = 1.0,
    path_prefixes: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
) -> None:
    """
    为 FastAPI 应用添加慢请求日志中间件（可选路径过滤）

    :param app: FastAPI 应用实例
    :param threshold: 慢请求阈值（秒），默认 1.0
    :param path_prefixes: 仅监控这些前缀的路径（如 ["/api"]），None 表示监控所有
    :param logger: 自定义日志器，None 则使用默认
    :param exclude_paths: 排除的路径列表（如 ["/health"]）
    """


    exclude_paths = exclude_paths or []
    path_prefixes = path_prefixes or []

    @app.middleware("http")
    async def slow_request_middleware(request: Request, call_next):
        # 跳过排除的路径
        for exclude in exclude_paths:
            if request.url.path.startswith(exclude):
                return await call_next(request)

        # 如果指定了 path_prefixes，只监控匹配的路径
        if path_prefixes:
            matched = any(request.url.path.startswith(prefix) for prefix in path_prefixes)
            if not matched:
                return await call_next(request)

        start_time = time.time()
        try:
            response: Response = await call_next(request)
        except Exception:
            # 即使出错也记录耗时
            process_time = time.time() - start_time
            if process_time > threshold:
                logger.log(
                    logging.ERROR,
                    f"Slow request (error): {request.method} {request.url.path} | "
                    f"Duration: {process_time:.3f}s | "
                    f"Client: {request.client.host if request.client else 'unknown'}"
                )
            raise

        process_time = time.time() - start_time

        if process_time > threshold:
            logger.log(
                logging.WARNING,
                f"Slow request: {request.method} {request.url.path} | "
                f"Duration: {process_time:.3f}s | "
                f"Status: {response.status_code} | "
                f"Client: {request.client.host if request.client else 'unknown'}"
            )

        return response
```

**code file end: nb_api/contrib/fastapi_helpers.py**

---


### code file start: nb_api/core/base.py 

```python
"""CRUD 路由生成器基类"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Optional, Type, Union
import time
import logging

from fastapi import APIRouter, HTTPException, Request, routing, Response
from fastapi.types import DecoratedCallable
from fastapi.responses import JSONResponse
from .types import T, DEPENDENCIES, ErrorResponseModel, ResponseModel
from .utils import pagination_factory, schema_factory

logger = logging.getLogger("nb_api")

NOT_FOUND = HTTPException(404, "Item not found")

class CustomRoute(routing.APIRoute):
    """
    自定义路由类,用于统一错误响应格式
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Any:
            try:
                return await original_route_handler(request)
            except HTTPException as exc:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"status_code": exc.status_code, "msg": str(exc.detail)},
                    headers=exc.headers
                )
        return custom_route_handler

class CRUDGenerator(Generic[T], APIRouter, ABC):
    """CRUD 路由生成器基类"""
    
    schema: Type[T]
    create_schema: Type[T]
    update_schema: Type[T]
    _base_path: str = "/"

    def __init__(
        self,
        schema: Type[T],
        create_schema: Optional[Type[T]] = None,
        update_schema: Optional[Type[T]] = None,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_all_route: Union[bool, DEPENDENCIES] = True,
        get_one_route: Union[bool, DEPENDENCIES] = True,
        create_route: Union[bool, DEPENDENCIES] = True,
        update_route: Union[bool, DEPENDENCIES] = True,
        delete_one_route: Union[bool, DEPENDENCIES] = True,
        delete_all_route: Union[bool, DEPENDENCIES] = True,
        search_route: Union[bool, DEPENDENCIES] = True,
        **kwargs: Any,
    ) -> None:
        self.schema = schema
        self.pagination = pagination_factory(max_limit=paginate)
        self._pk: str = self._pk if hasattr(self, "_pk") else "id"
        
        # 创建 create_schema 和 update_schema
        self.create_schema = (
            create_schema
            if create_schema
            else schema_factory(self.schema, pk_field_name=self._pk, name="Create")
        )
        self.update_schema = (
            update_schema
            if update_schema
            else schema_factory(self.schema, pk_field_name=self._pk, name="Update")
        )

        # 设置路由前缀
        prefix = str(prefix if prefix else self.schema.__name__).lower()
        prefix = self._base_path + prefix.strip("/")
        tags = tags or [prefix.strip("/").capitalize()]

        super().__init__(prefix=prefix, tags=tags, route_class=CustomRoute, **kwargs)
        # 注册路由
        if get_all_route:
            self._add_api_route(
                "",
                self._get_all(),
                methods=["GET"],
                response_model=ResponseModel[List[self.schema]],  # type: ignore
                summary="Get All",
                dependencies=get_all_route,
            )

        if create_route:
            self._add_api_route(
                "",
                self._create(),
                methods=["POST"],
                response_model=ResponseModel[self.schema],
                summary="Create One",
                dependencies=create_route,
            )

        if delete_all_route:
            self._add_api_route(
                "",
                self._delete_all(),
                methods=["DELETE"],
                response_model=ResponseModel[List[self.schema]],  # type: ignore
                summary="Delete All",
                dependencies=delete_all_route,
            )

        if get_one_route:
            self._add_api_route(
                "/{item_id}",
                self._get_one(),
                methods=["GET"],
                response_model=ResponseModel[self.schema],
                summary="Get One",
                dependencies=get_one_route,
                error_responses=[NOT_FOUND],
            )

        if update_route:
            self._add_api_route(
                "/{item_id}",
                self._update(),
                methods=["PUT"],
                response_model=ResponseModel[self.schema],
                summary="Update One",
                dependencies=update_route,
                error_responses=[NOT_FOUND],
            )

        if delete_one_route:
            self._add_api_route(
                "/{item_id}",
                self._delete_one(),
                methods=["DELETE"],
                response_model=ResponseModel[self.schema],
                summary="Delete One",
                dependencies=delete_one_route,
                error_responses=[NOT_FOUND],
            )

        if search_route:
            # 注册 search 路由
            self._add_api_route(
                "/search",
                self._search(),
                methods=["POST"],
                response_model=ResponseModel[List[self.schema]],  # type: ignore
                summary="Search",
                dependencies=search_route,
            )

    def _add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        dependencies: Union[bool, DEPENDENCIES],
        error_responses: Optional[List[HTTPException]] = None,
        **kwargs: Any,
    ) -> None:
        """添加 API 路由"""
        dependencies = [] if isinstance(dependencies, bool) else dependencies
        responses: Any = {}
        if error_responses:
            for err in error_responses:
                responses[err.status_code] = {
                    "model": ErrorResponseModel,
                    "content": {
                        "application/json": {"example": {"status_code": err.status_code, "msg": err.detail}}
                    },
                }
        super().add_api_route(
            path, endpoint, dependencies=dependencies, responses=responses, **kwargs
        )

    def api_route(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """覆盖已存在的路由"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["GET"])
        return super().get(path, *args, **kwargs)

    def post(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        """移除 API 路由"""
        methods_ = set(methods)

        for route in self.routes:
            if (
                route.path == f"{self.prefix}{path}"  # type: ignore
                and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)

    @abstractmethod
    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """获取所有记录"""
        raise NotImplementedError

    @abstractmethod
    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """获取单条记录"""
        raise NotImplementedError

    @abstractmethod
    def _create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """创建记录"""
        raise NotImplementedError

    @abstractmethod
    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """更新记录"""
        raise NotImplementedError

    @abstractmethod
    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """删除单条记录"""
        raise NotImplementedError

    @abstractmethod
    def _delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """删除所有记录"""
        raise NotImplementedError

    @abstractmethod
    def _search(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """搜索记录"""
        raise NotImplementedError

    def _raise(self, e: Exception, status_code: int = 422) -> HTTPException:
        """抛出 HTTP 异常"""
        raise HTTPException(status_code, ", ".join(e.args)) from e

    @staticmethod
    def get_routes() -> List[str]:
        """获取所有路由名称"""
        return ["get_all", "create", "delete_all", "get_one", "update", "delete_one", "search"]

```

**code file end: nb_api/core/base.py**

---


### code file start: nb_api/core/mem.py 

```python
# """内存 CRUD 路由器 (用于快速原型开发和测试)"""

# from typing import Any, Callable, List, Type, cast, Optional, Union

# from . import CRUDGenerator, NOT_FOUND
# from ._types import DEPENDENCIES, PAGINATION, PYDANTIC_SCHEMA as SCHEMA

# CALLABLE = Callable[..., SCHEMA]
# CALLABLE_LIST = Callable[..., List[SCHEMA]]


# class MemoryCRUDRouter(CRUDGenerator[SCHEMA]):
#     """内存 CRUD 路由器"""
    
#     def __init__(
#         self,
#         schema: Type[SCHEMA],
#         create_schema: Optional[Type[SCHEMA]] = None,
#         update_schema: Optional[Type[SCHEMA]] = None,
#         prefix: Optional[str] = None,
#         tags: Optional[List[str]] = None,
#         paginate: Optional[int] = None,
#         get_all_route: Union[bool, DEPENDENCIES] = True,
#         get_one_route: Union[bool, DEPENDENCIES] = True,
#         create_route: Union[bool, DEPENDENCIES] = True,
#         update_route: Union[bool, DEPENDENCIES] = True,
#         delete_one_route: Union[bool, DEPENDENCIES] = True,
#         delete_all_route: Union[bool, DEPENDENCIES] = True,
#         **kwargs: Any
#     ) -> None:
#         super().__init__(
#             schema=schema,
#             create_schema=create_schema,
#             update_schema=update_schema,
#             prefix=prefix,
#             tags=tags,
#             paginate=paginate,
#             get_all_route=get_all_route,
#             get_one_route=get_one_route,
#             create_route=create_route,
#             update_route=update_route,
#             delete_one_route=delete_one_route,
#             delete_all_route=delete_all_route,
#             **kwargs
#         )

#         self.models: List[SCHEMA] = []
#         self._id = 1

#     def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
#         def route(pagination: PAGINATION = self.pagination) -> List[SCHEMA]:
#             skip, limit = pagination.get("skip"), pagination.get("limit")
#             skip = cast(int, skip)

#             return (
#                 self.models[skip:]
#                 if limit is None
#                 else self.models[skip : skip + limit]
#             )

#         return route

#     def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
#         def route(item_id: int) -> SCHEMA:
#             for model in self.models:
#                 if getattr(model, "id") == item_id:
#                     return model

#             raise NOT_FOUND

#         return route

#     def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
#         def route(model: self.create_schema) -> SCHEMA:  # type: ignore
#             model_dict = model.model_dump()
#             model_dict["id"] = self._get_next_id()
#             ready_model = self.schema(**model_dict)
#             self.models.append(ready_model)
#             return ready_model

#         return route

#     def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
#         def route(item_id: int, model: self.update_schema) -> SCHEMA:  # type: ignore
#             for ind, model_ in enumerate(self.models):
#                 if getattr(model_, "id") == item_id:
#                     self.models[ind] = self.schema(
#                         **model.model_dump(), id=getattr(model_, "id")
#                     )
#                     return self.models[ind]

#             raise NOT_FOUND

#         return route

#     def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
#         def route() -> List[SCHEMA]:
#             self.models = []
#             return self.models

#         return route

#     def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
#         def route(item_id: int) -> SCHEMA:
#             for ind, model in enumerate(self.models):
#                 if getattr(model, "id") == item_id:
#                     del self.models[ind]
#                     return model

#             raise NOT_FOUND

#         return route

#     def _get_next_id(self) -> int:
#         """获取下一个 ID"""
#         id_ = self._id
#         self._id += 1
#         return id_


```

**code file end: nb_api/core/mem.py**

---


### code file start: nb_api/core/sqlmodel.py 

```python
"""SQLModel CRUD 路由器"""

from typing import Any, Callable, List, Type, Generator, Optional, Union, Dict, Literal

from fastapi import Depends, HTTPException

from .base import CRUDGenerator, NOT_FOUND
from .types import DEPENDENCIES, PAGINATION, PYDANTIC_SCHEMA as SCHEMA, BaseModel, ResponseModel, CALLABLE, CALLABLE_LIST, SearchRequest, Sorting
from .utils import get_pk_type

try:
    from sqlmodel import Session, select
    from sqlalchemy.exc import IntegrityError
except ImportError:
    Session = None  # type: ignore
    IntegrityError = None  # type: ignore
    select = None  # type: ignore
    sqlmodel_installed = False
else:
    sqlmodel_installed = True
    Session = Callable[..., Generator[Session, Any, None]]






class SQLModelCRUDRouter(CRUDGenerator[SCHEMA]):
    """SQLModel CRUD 路由器"""
    
    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Type[Any],
        db: Session,
        create_schema: Optional[Type[SCHEMA]] = None,
        update_schema: Optional[Type[SCHEMA]] = None,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_all_route: Union[bool, DEPENDENCIES] = True,
        get_one_route: Union[bool, DEPENDENCIES] = True,
        create_route: Union[bool, DEPENDENCIES] = True,
        update_route: Union[bool, DEPENDENCIES] = True,
        delete_one_route: Union[bool, DEPENDENCIES] = True,
        delete_all_route: Union[bool, DEPENDENCIES] = True,
        search_route: Union[bool, DEPENDENCIES] = True,
        **kwargs: Any
    ) -> None:
        assert (
            sqlmodel_installed
        ), "SQLModel must be installed to use the SQLModelCRUDRouter."

        self.db_model = db_model
        self.db_func = db
        
        # 获取主键字段名
        try:
            # SQLModel 模型的主键通常是第一个标记为 primary_key 的字段
            self._pk: str = "id"  # 默认主键
            for field_name, field_info in db_model.model_fields.items():
                # 检查字段的 sa_column 属性
                if hasattr(field_info, 'sa_column') and field_info.sa_column is not None:
                    if getattr(field_info.sa_column, 'primary_key', False):
                        self._pk = field_name
                        break
        except Exception:
            self._pk = "id"
            
        self._pk_type: type = get_pk_type(schema, self._pk)

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix or getattr(db_model, "__tablename__", db_model.__name__.lower()),
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            search_route=search_route,
            **kwargs
        )

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        def route(
            db: Session = Depends(self.db_func),
            pagination: PAGINATION = self.pagination,
        ) -> ResponseModel[List[Any]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            statement = select(self.db_model).offset(skip).limit(limit)
            db_models = db.exec(statement).all()
            return ResponseModel(data=list(db_models))

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self._pk_type, db: Session = Depends(self.db_func)  # type: ignore
        ) -> Any:
            model: Optional[SCHEMA] = db.get(self.db_model, item_id)

            if model:
                return ResponseModel(data=model)
            else:
                raise NOT_FOUND

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            model: self.create_schema,  # type: ignore
            db: Session = Depends(self.db_func),
        ) -> Any:
            try:
                db_model = self.db_model(**model.model_dump())
                db.add(db_model)
                db.commit()
                db.refresh(db_model)
                return ResponseModel(data=db_model)
            except IntegrityError:
                db.rollback()
                raise HTTPException(422, "Key already exists") from None

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self._pk_type,  # type: ignore
            model: self.update_schema,  # type: ignore
            db: Session = Depends(self.db_func),
        ) -> Any:
            try:
                response = self._get_one()(item_id, db)
                db_model = response.data

                # 使用 exclude_unset=True 只更新实际提供的字段
                for key, value in model.model_dump(exclude_unset=True, exclude={self._pk}).items():
                    if hasattr(db_model, key):
                        setattr(db_model, key, value)

                db.add(db_model)
                db.commit()
                db.refresh(db_model)

                return ResponseModel(data=db_model)
            except IntegrityError as e:
                db.rollback()
                self._raise(e)

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        def route(db: Session = Depends(self.db_func)) -> ResponseModel[List[Any]]:
            statement = select(self.db_model)
            models = db.exec(statement).all()
            for model in models:
                db.delete(model)
            db.commit()

            return ResponseModel(data=[])

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(
            item_id: self._pk_type, db: Session = Depends(self.db_func)  # type: ignore
        ) -> Any:
            response = self._get_one()(item_id, db)
            db_model = response.data
            db.delete(db_model)
            db.commit()

            return ResponseModel(data=db_model)

        return route

    def _search(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        """实现超级搜索路由"""
        def route(
            search_params: SearchRequest,
            db: Session = Depends(self.db_func),
            pagination: PAGINATION = self.pagination,
        ) -> ResponseModel[List[Any]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            statement = select(self.db_model)

            # 1. 应用过滤器 (filters)
            if search_params.filters:
                for f in search_params.filters:
                    if not hasattr(self.db_model, f.field):
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid filter field: '{f.field}' is not a valid field for {self.db_model.__name__}."
                        )
                    
                    column = getattr(self.db_model, f.field)

                    if f.operator == "gt":
                        statement = statement.where(column > f.value)
                    elif f.operator == "lt":
                        statement = statement.where(column < f.value)
                    elif f.operator == "eq":
                        statement = statement.where(column == f.value)
                    elif f.operator == "ne":
                        statement = statement.where(column != f.value)
                    elif f.operator == "contains":
                        statement = statement.where(column.contains(f.value))
                    elif f.operator == "in":
                        statement = statement.where(column.in_(f.value))

            # 2. 应用排序 (sorting)
            if search_params.sorting:
                for s in search_params.sorting:
                    if not hasattr(self.db_model, s.field):
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid sorting field: '{s.field}' is not a valid field for {self.db_model.__name__}."
                        )
                    column = getattr(self.db_model, s.field)
                    statement = statement.order_by(column.desc() if s.direction == "desc" else column.asc())

            statement = statement.offset(skip).limit(limit)
            db_models = db.exec(statement).all()
            return ResponseModel(data=list(db_models))

        return route

```

**code file end: nb_api/core/sqlmodel.py**

---


### code file start: nb_api/core/types.py 

```python
"""类型定义"""

from typing import Any, Callable, Dict, Generic, List, Literal, TypeVar, Optional, Sequence
from fastapi.params import Depends
from pydantic import BaseModel
from pydantic.generics import GenericModel

PAGINATION = Dict[str, Optional[int]]
PYDANTIC_SCHEMA = BaseModel

T = TypeVar("T")
DEPENDENCIES = Optional[Sequence[Depends]]

class ResponseModel(GenericModel, Generic[T]):
    """统一响应模型"""
    status_code: int = 0
    msg: str = "success"
    data: Optional[T] = None

class ErrorResponseModel(GenericModel):
    """错误响应模型"""
    status_code: int
    msg: str


def gen_resp(data: T) -> ResponseModel[T]:
    return ResponseModel(data=data)

def gen_err_resp(status_code: int, msg: str) -> ErrorResponseModel:
    return ErrorResponseModel(status_code=status_code, msg=msg)


CALLABLE = Callable[..., Any]
CALLABLE_LIST = Callable[..., List[Any]]

# --- 超级搜索接口的模型定义 ---

# 定义支持的查询操作符
Operator = Literal["gt", "lt", "eq", "ne", "contains", "in"]

# 定义支持的排序方向
Direction = Literal["asc", "desc"]

class Filter(BaseModel):
    field: str
    operator: Operator
    value: Any

class Sorting(BaseModel):
    field: str
    direction: Direction

class SearchRequest(BaseModel):
    filters: Optional[List[Filter]] = None
    sorting: Optional[List[Sorting]] = None
```

**code file end: nb_api/core/types.py**

---


### code file start: nb_api/core/utils.py 

```python
"""工具函数"""

from typing import Optional, Type, Any
from fastapi import Depends, HTTPException
from pydantic import BaseModel, create_model

from .types import T, PAGINATION, PYDANTIC_SCHEMA


class AttrDict(dict):  # type: ignore
    """支持属性访问的字典"""
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def get_pk_type(schema: Type[PYDANTIC_SCHEMA], pk_field: str) -> Any:
    """获取主键字段类型"""
    try:
        return schema.model_fields[pk_field].annotation
    except (KeyError, AttributeError):
        return int


def schema_factory(
    schema_cls: Type[T], pk_field_name: str = "id", name: str = "Create"
) -> Type[T]:
    """
    创建一个不包含主键的 Schema (用于 Create/Update)
    """
    fields = {}
    try:
        # Pydantic v2
        for field_name, field_info in schema_cls.model_fields.items():
            if field_name != pk_field_name:
                annotation = field_info.annotation
                # 检查是否有默认值
                if hasattr(field_info, 'default') and field_info.default is not None:
                    from pydantic_core import PydanticUndefined
                    if field_info.default is not PydanticUndefined:
                        default = field_info.default
                    else:
                        default = ...
                else:
                    default = ...
                fields[field_name] = (annotation, default)
    except AttributeError:
        # Pydantic v1 fallback
        for field_name, field in schema_cls.__fields__.items():
            if field_name != pk_field_name:
                fields[field_name] = (field.outer_type_, field.default if field.default is not None else ...)

    model_name = schema_cls.__name__ + name
    schema: Type[T] = create_model(model_name, **fields)  # type: ignore
    return schema


def create_query_validation_exception(field: str, msg: str) -> HTTPException:
    """创建查询参数验证异常"""
    return HTTPException(
        422,
        detail={
            "detail": [
                {"loc": ["query", field], "msg": msg, "type": "type_error.integer"}
            ]
        },
    )


def pagination_factory(max_limit: Optional[int] = None) -> Any:
    """
    创建分页依赖
    """

    def pagination(skip: int = 0, limit: Optional[int] = max_limit) -> PAGINATION:
        if skip < 0:
            raise create_query_validation_exception(
                field="skip",
                msg="skip query parameter must be greater or equal to zero",
            )

        if limit is not None:
            if limit <= 0:
                raise create_query_validation_exception(
                    field="limit", msg="limit query parameter must be greater then zero"
                )

            elif max_limit and max_limit < limit:
                raise create_query_validation_exception(
                    field="limit",
                    msg=f"limit query parameter must be less then {max_limit}",
                )

        return {"skip": skip, "limit": limit}

    return Depends(pagination)


```

**code file end: nb_api/core/utils.py**

---


### code file start: nb_api/core/__init__.py 

```python
"""核心模块"""




```

**code file end: nb_api/core/__init__.py**

---

