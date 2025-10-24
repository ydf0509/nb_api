"""类型定义"""

from typing import Any, Callable, Dict, Generic, List, Literal, TypeVar, Optional, Sequence
from fastapi.params import Depends
from pydantic import BaseModel
# from pydantic.generics import GenericModel

PAGINATION = Dict[str, Optional[int]]
PYDANTIC_SCHEMA = BaseModel

T = TypeVar("T")
DEPENDENCIES = Optional[Sequence[Depends]]

class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    status_code: int = 0
    msg: str = "success"
    data: Optional[T] = None

class ErrorResponseModel(BaseModel):
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