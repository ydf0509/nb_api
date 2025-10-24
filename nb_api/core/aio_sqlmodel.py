"""异步 SQLModel CRUD 路由器"""

from typing import Any, Callable, List, Type, AsyncGenerator, Optional, Union, Dict, Literal
from functools import wraps

from fastapi import Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from .base import CRUDGenerator, NOT_FOUND
from .types import DEPENDENCIES, PAGINATION, PYDANTIC_SCHEMA as SCHEMA, BaseModel, ResponseModel, CALLABLE, CALLABLE_LIST, SearchRequest, Sorting
from .utils import get_pk_type


def get_primary_key(db_model: Any) -> str:
    """获取 SQLModel 模型的主键字段名"""
    try:
        # SQLModel 模型的主键通常是第一个标记为 primary_key 的字段
        for field_name, field_info in db_model.model_fields.items():
            # 检查字段的 sa_column 属性
            if hasattr(field_info, 'sa_column') and field_info.sa_column is not None:
                if getattr(field_info.sa_column, 'primary_key', False):
                    return field_name
        return "id"  # 默认主键
    except Exception:
        return "id"


class AioSQLModelCRUDRouter(CRUDGenerator[SCHEMA]):
    """异步 SQLModel CRUD 路由器"""
    
    def __init__(
        self,
        schema: Type[SCHEMA],
        db_model: Type[Any],
        db: Callable[..., AsyncGenerator[AsyncSession, None]],  # 异步数据库会话依赖
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
        self.db_func = db
        
        # 获取主键字段名
        self._pk: str = get_primary_key(db_model)
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
        async def route(
            db: AsyncSession = Depends(self.db_func),
            pagination: PAGINATION = self.pagination,
        ) -> ResponseModel[List[Any]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            statement = select(self.db_model).offset(skip).limit(limit)
            result = await db.execute(statement)
            db_models = result.scalars().all()
            return ResponseModel(data=list(db_models))

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: AsyncSession = Depends(self.db_func)  # type: ignore
        ) -> Any:
            statement = select(self.db_model).where(getattr(self.db_model, self._pk) == item_id)
            result = await db.execute(statement)
            model = result.scalar_one_or_none()

            if model:
                return ResponseModel(data=model)
            else:
                raise NOT_FOUND

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            db: AsyncSession = Depends(self.db_func),
        ) -> Any:
            try:
                db_model = self.db_model(**model.model_dump())
                db.add(db_model)
                await db.commit()
                await db.refresh(db_model)
                return ResponseModel(data=db_model)
            except IntegrityError:
                await db.rollback()
                raise HTTPException(422, "Key already exists") from None

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            model: self.update_schema,  # type: ignore
            db: AsyncSession = Depends(self.db_func),
        ) -> Any:
            try:
                # 获取现有模型
                statement = select(self.db_model).where(getattr(self.db_model, self._pk) == item_id)
                result = await db.execute(statement)
                db_model = result.scalar_one_or_none()
                
                if not db_model:
                    raise NOT_FOUND

                # 使用 exclude_unset=True 只更新实际提供的字段
                for key, value in model.model_dump(exclude_unset=True, exclude={self._pk}).items():
                    if hasattr(db_model, key):
                        setattr(db_model, key, value)

                db.add(db_model)
                await db.commit()
                await db.refresh(db_model)

                return ResponseModel(data=db_model)
            except IntegrityError as e:
                await db.rollback()
                self._raise(e)

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(db: AsyncSession = Depends(self.db_func)) -> ResponseModel[List[Any]]:
            statement = select(self.db_model)
            result = await db.execute(statement)
            models = result.scalars().all()
            for model in models:
                await db.delete(model)
            await db.commit()

            return ResponseModel(data=[])

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: AsyncSession = Depends(self.db_func)  # type: ignore
        ) -> Any:
            statement = select(self.db_model).where(getattr(self.db_model, self._pk) == item_id)
            result = await db.execute(statement)
            db_model = result.scalar_one_or_none()
            
            if not db_model:
                raise NOT_FOUND
                
            await db.delete(db_model)
            await db.commit()

            return ResponseModel(data=db_model)

        return route

    def _search(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        """实现超级搜索路由"""
        async def route(
            search_params: SearchRequest,
            db: AsyncSession = Depends(self.db_func),
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
            result = await db.execute(statement)
            db_models = result.scalars().all()
            return ResponseModel(data=list(db_models))

        return route