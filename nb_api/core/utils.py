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

