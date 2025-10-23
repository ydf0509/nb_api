"""nb_api - 基于 FastAPI + Pydantic v2 + SQLModel 的自动 CRUD 路由生成框架"""

# from .core import (
#     CRUDGenerator,
#     SQLModelCRUDRouter,
#     MemoryCRUDRouter,
# )


from .core.base import CRUDGenerator
from .core.sqlmodel import SQLModelCRUDRouter
from .version import __version__

