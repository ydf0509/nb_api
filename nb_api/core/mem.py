"""内存 CRUD 路由器 (用于快速原型开发和测试)"""

from typing import Any, Callable, List, Type, Optional, Union, Dict, Literal, cast
from functools import wraps

from fastapi import HTTPException

from .base import CRUDGenerator, NOT_FOUND
from .types import DEPENDENCIES, PAGINATION, PYDANTIC_SCHEMA as SCHEMA, BaseModel, ResponseModel, CALLABLE, CALLABLE_LIST, SearchRequest, Sorting

# 全局存储所有内存模型的字典
_memory_stores: Dict[str, List[SCHEMA]] = {}
_id_counters: Dict[str, int] = {}


class MemoryCRUDRouter(CRUDGenerator[SCHEMA]):
    """内存 CRUD 路由器"""
    
    def __init__(
        self,
        schema: Type[SCHEMA],
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
        # 初始化内存存储
        self.store_key = prefix or schema.__name__.lower()
        if self.store_key not in _memory_stores:
            _memory_stores[self.store_key] = []
            _id_counters[self.store_key] = 1
            
        self.models = _memory_stores[self.store_key]
        self._id_counter_key = self.store_key

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix,
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

    def _get_next_id(self) -> int:
        """获取下一个 ID"""
        current_id = _id_counters[self._id_counter_key]
        _id_counters[self._id_counter_key] += 1
        return current_id

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        def route(
            pagination: PAGINATION = self.pagination
        ) -> ResponseModel[List[SCHEMA]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")
            skip = cast(int, skip)

            if limit is None:
                result = self.models[skip:]
            else:
                result = self.models[skip : skip + limit]
                
            return ResponseModel(data=result)

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(item_id: int) -> Any:
            for model in self.models:
                if getattr(model, "id", None) == item_id:
                    return ResponseModel(data=model)
            raise NOT_FOUND

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(model: self.create_schema) -> Any:  # type: ignore
            model_dict = model.model_dump()
            
            # 如果没有提供 id，则自动生成
            if "id" not in model_dict or model_dict["id"] is None:
                model_dict["id"] = self._get_next_id()
                
            ready_model = self.schema(**model_dict)
            self.models.append(ready_model)
            return ResponseModel(data=ready_model)

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(item_id: int, model: self.update_schema) -> Any:  # type: ignore
            for ind, model_ in enumerate(self.models):
                if getattr(model_, "id") == item_id:
                    # 更新模型数据
                    update_data = model.model_dump(exclude_unset=True)
                    model_dict = model_.model_dump()
                    model_dict.update(update_data)
                    # 保持原有的 id
                    model_dict["id"] = item_id
                    self.models[ind] = self.schema(**model_dict)
                    return ResponseModel(data=self.models[ind])
            raise NOT_FOUND

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        def route() -> ResponseModel[List[SCHEMA]]:
            deleted = self.models.copy()
            self.models.clear()
            # 重置 ID 计数器
            _id_counters[self._id_counter_key] = 1
            return ResponseModel(data=deleted)

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        def route(item_id: int) -> Any:
            for ind, model in enumerate(self.models):
                if getattr(model, "id") == item_id:
                    deleted_model = self.models.pop(ind)
                    return ResponseModel(data=deleted_model)
            raise NOT_FOUND

        return route

    def _search(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        """实现超级搜索路由"""
        def route(
            search_params: SearchRequest,
            pagination: PAGINATION = self.pagination,
        ) -> ResponseModel[List[SCHEMA]]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            # 开始时获取所有模型
            filtered_models = self.models.copy()

            # 1. 应用过滤器 (filters)
            if search_params.filters:
                for f in search_params.filters:
                    if f.field not in self.schema.model_fields:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid filter field: '{f.field}' is not a valid field for {self.schema.__name__}."
                        )

                    # 过滤模型
                    new_filtered_models = []
                    for model in filtered_models:
                        model_value = getattr(model, f.field, None)
                        if model_value is None:
                            continue
                            
                        if f.operator == "eq" and model_value == f.value:
                            new_filtered_models.append(model)
                        elif f.operator == "ne" and model_value != f.value:
                            new_filtered_models.append(model)
                        elif f.operator == "gt" and model_value > f.value:
                            new_filtered_models.append(model)
                        elif f.operator == "lt" and model_value < f.value:
                            new_filtered_models.append(model)
                        elif f.operator == "contains" and isinstance(model_value, str) and f.value in model_value:
                            new_filtered_models.append(model)
                        elif f.operator == "in" and model_value in f.value:
                            new_filtered_models.append(model)
                    
                    filtered_models = new_filtered_models

            # 2. 应用排序 (sorting)
            if search_params.sorting:
                for s in reversed(search_params.sorting):  # 反向应用排序以获得正确的顺序
                    if s.field not in self.schema.model_fields:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid sorting field: '{s.field}' is not a valid field for {self.schema.__name__}."
                        )
                    
                    # 排序
                    reverse = (s.direction == "desc")
                    filtered_models.sort(key=lambda x: getattr(x, s.field, 0), reverse=reverse)

            # 应用分页
            if limit is None:
                result = filtered_models[skip:]
            else:
                result = filtered_models[skip : skip + limit]
                
            return ResponseModel(data=result)

        return route