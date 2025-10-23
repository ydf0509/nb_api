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
