"""Tortoise ORM CRUD 路由器"""

from typing import Any, Callable, List, Type, Optional, Union, Dict, Literal
import asyncio

from fastapi import Depends, HTTPException
from tortoise.models import Model as TortoiseModel
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch
from tortoise import Tortoise

from .base import CRUDGenerator, NOT_FOUND
from .types import DEPENDENCIES, PAGINATION, PYDANTIC_SCHEMA as SCHEMA, BaseModel, ResponseModel, CALLABLE, CALLABLE_LIST, SearchRequest, Sorting
from .utils import get_pk_type


def get_primary_key(db_model: Type[TortoiseModel]) -> str:
    """获取 Tortoise ORM 模型的主键字段名"""
    try:
        # Tortoise ORM 中主键字段名为 pk
        for field_name, field_obj in db_model._meta.fields_map.items():
            if field_obj.pk:
                return field_name
        return "id"  # 默认主键
    except Exception:
        return "id"


class TortoiseCRUDRouter(CRUDGenerator[SCHEMA]):
    """Tortoise ORM CRUD 路由器"""
    
    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Type[TortoiseModel],
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
        self.db_model = db_model
        
        # 获取主键字段名
        self._pk: str = get_primary_key(db_model)
        self._pk_type: type = get_pk_type(schema, self._pk)

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix or getattr(db_model, "__name__", db_model.__name__.lower()),
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
        async def route(
            pagination: PAGINATION = self.pagination,
        ) -> ResponseModel[List[Any]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            query = self.db_model.all().offset(skip).limit(limit)
            db_models = await query
            return ResponseModel(data=list(db_models))

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
        ) -> Any:
            db_model = await self.db_model.get_or_none(**{self._pk: item_id})
            
            if db_model:
                return ResponseModel(data=db_model)
            else:
                raise NOT_FOUND

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
        ) -> Any:
            try:
                db_model = await self.db_model.create(**model.model_dump())
                return ResponseModel(data=db_model)
            except IntegrityError:
                raise HTTPException(422, "Key already exists") from None

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            model: self.update_schema,  # type: ignore
        ) -> Any:
            try:
                # 获取现有模型
                db_model = await self.db_model.get_or_none(**{self._pk: item_id})
                if not db_model:
                    raise NOT_FOUND

                # 使用 exclude_unset=True 只更新实际提供的字段
                update_data = model.model_dump(exclude_unset=True, exclude={self._pk})
                for key, value in update_data.items():
                    setattr(db_model, key, value)

                await db_model.save()
                return ResponseModel(data=db_model)
            except IntegrityError as e:
                self._raise(e)

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route() -> ResponseModel[List[Any]]:
            db_models = await self.db_model.all()
            # 在 Tortoise ORM 中，删除所有记录
            await self.db_model.filter().delete()
            return ResponseModel(data=[])

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
        ) -> Any:
            db_model = await self.db_model.get_or_none(**{self._pk: item_id})
            if not db_model:
                raise NOT_FOUND
                
            await db_model.delete()
            return ResponseModel(data=db_model)

        return route

    def _search(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        """实现超级搜索路由"""
        async def route(
            search_params: SearchRequest,
            pagination: PAGINATION = self.pagination,
        ) -> ResponseModel[List[Any]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            # 构建查询
            query = self.db_model.all()

            # 1. 应用过滤器 (filters)
            if search_params.filters:
                q_objects = []
                for f in search_params.filters:
                    if f.field not in self.db_model._meta.fields_map:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid filter field: '{f.field}' is not a valid field for {self.db_model.__name__}."
                        )

                    # 构建 Q 对象
                    field_lookup = f"{f.field}__{f.operator}"
                    if f.operator == "eq":
                        field_lookup = f.field  # 等于操作不需要后缀
                    elif f.operator == "ne":
                        field_lookup = f"{f.field}__not"
                    elif f.operator == "gt":
                        field_lookup = f"{f.field}__gt"
                    elif f.operator == "lt":
                        field_lookup = f"{f.field}__lt"
                    elif f.operator == "contains":
                        field_lookup = f"{f.field}__icontains"
                    elif f.operator == "in":
                        field_lookup = f"{f.field}__in"

                    q_objects.append(Q(**{field_lookup: f.value}))

                # 应用所有 Q 对象
                if q_objects:
                    query = query.filter(*q_objects)

            # 2. 应用排序 (sorting)
            if search_params.sorting:
                ordering = []
                for s in search_params.sorting:
                    if s.field not in self.db_model._meta.fields_map:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid sorting field: '{s.field}' is not a valid field for {self.db_model.__name__}."
                        )
                    prefix = "-" if s.direction == "desc" else ""
                    ordering.append(f"{prefix}{s.field}")
                
                if ordering:
                    query = query.order_by(*ordering)

            # 应用分页
            query = query.offset(skip).limit(limit)
            db_models = await query
            return ResponseModel(data=list(db_models))

        return route