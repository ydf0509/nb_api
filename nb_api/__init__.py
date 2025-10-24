"""nb_api - 基于 FastAPI + Pydantic v2 + SQLModel 的自动 CRUD 路由生成框架"""

# from .core import (
#     CRUDGenerator,
#     SQLModelCRUDRouter,
#     MemoryCRUDRouter,
# )


from .core.base import CRUDGenerator
from .core.sqlmodel import SQLModelCRUDRouter
from .core.sqlalchemy import SQLAlchemyCRUDRouter
from .core.aio_sqlmodel import AioSQLModelCRUDRouter
# 为了保持nb_api三方包依赖少,用户要使用tortoise自己导入 from nb_api.core.tortoise import TortoiseCRUDRouter 
from .core.tortoise import TortoiseCRUDRouter  
from .core.mem import MemoryCRUDRouter

