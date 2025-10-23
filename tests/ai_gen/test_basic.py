"""基础功能测试"""

from fastapi.testclient import TestClient
from pydantic import BaseModel
from fastapi import FastAPI
from nb_api import MemoryCRUDRouter


class Item(BaseModel):
    """测试项目模型"""
    id: int
    name: str
    price: float


def test_memory_crud_basic():
    """测试内存 CRUD 基本功能"""
    app = FastAPI()
    router = MemoryCRUDRouter(schema=Item)
    app.include_router(router)
    
    client = TestClient(app)
    
    # 测试 GET 所有 (应该为空)
    response = client.get("/item")
    assert response.status_code == 200
    assert response.json() == []
    
    # 测试 POST 创建
    item_data = {"name": "测试商品", "price": 99.99}
    response = client.post("/item", json=item_data)
    assert response.status_code == 200
    created_item = response.json()
    assert created_item["name"] == "测试商品"
    assert created_item["price"] == 99.99
    assert "id" in created_item
    item_id = created_item["id"]
    
    # 测试 GET 单个
    response = client.get(f"/item/{item_id}")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == item_id
    assert item["name"] == "测试商品"
    
    # 测试 PUT 更新
    update_data = {"name": "更新商品", "price": 199.99}
    response = client.put(f"/item/{item_id}", json=update_data)
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["name"] == "更新商品"
    assert updated_item["price"] == 199.99
    
    # 测试 DELETE 单个
    response = client.delete(f"/item/{item_id}")
    assert response.status_code == 200
    
    # 验证已删除
    response = client.get(f"/item/{item_id}")
    assert response.status_code == 404
    
    print("✅ 所有测试通过!")


def test_pagination():
    """测试分页功能"""
    app = FastAPI()
    router = MemoryCRUDRouter(schema=Item, paginate=5)
    app.include_router(router)
    
    client = TestClient(app)
    
    # 创建多个项目
    for i in range(10):
        client.post("/item", json={"name": f"商品{i}", "price": i * 10.0})
    
    # 测试分页
    response = client.get("/item?skip=0&limit=5")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 5
    
    response = client.get("/item?skip=5&limit=5")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 5
    
    # 测试超出最大限制
    response = client.get("/item?skip=0&limit=10")
    assert response.status_code == 422  # 超出 paginate 限制
    
    print("✅ 分页测试通过!")


def test_route_disable():
    """测试禁用特定路由"""
    app = FastAPI()
    router = MemoryCRUDRouter(
        schema=Item,
        delete_all_route=False,  # 禁用删除所有
        update_route=False       # 禁用更新
    )
    app.include_router(router)
    
    client = TestClient(app)
    
    # 创建一个项目
    response = client.post("/item", json={"name": "测试", "price": 10.0})
    item_id = response.json()["id"]
    
    # 测试禁用的路由
    response = client.delete("/item")
    assert response.status_code == 405  # Method Not Allowed
    
    response = client.put(f"/item/{item_id}", json={"name": "更新", "price": 20.0})
    assert response.status_code == 405  # Method Not Allowed
    
    # 其他路由应该正常工作
    response = client.get("/item")
    assert response.status_code == 200
    
    response = client.get(f"/item/{item_id}")
    assert response.status_code == 200
    
    print("✅ 路由禁用测试通过!")


if __name__ == "__main__":
    test_memory_crud_basic()
    test_pagination()
    test_route_disable()
    print("\n🎉 所有测试完成!")

