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
