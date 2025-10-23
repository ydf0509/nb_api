"""SQLModel CRUD 功能测试"""

from typing import Optional
from fastapi.testclient import TestClient
from sqlmodel import Field, Session, SQLModel, create_engine
from fastapi import FastAPI
from nb_api import SQLModelCRUDRouter


# 定义测试模型
class Product(SQLModel, table=True):
    """产品模型"""
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float
    stock: int = Field(default=0)


class ProductRead(SQLModel):
    """产品读取模型"""
    id: int
    name: str
    price: float
    stock: int


class ProductCreate(SQLModel):
    """产品创建模型"""
    name: str
    price: float
    stock: int = 0


class ProductUpdate(SQLModel):
    """产品更新模型"""
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


def create_test_app():
    """创建测试应用"""
    # 使用内存数据库
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    def get_session():
        with Session(engine) as session:
            yield session
    
    app = FastAPI()
    router = SQLModelCRUDRouter(
        schema=ProductRead,
        create_schema=ProductCreate,
        update_schema=ProductUpdate,
        db_model=Product,
        db=get_session,
        prefix="products",
        paginate=10
    )
    app.include_router(router)
    
    return app


def test_sqlmodel_crud_basic():
    """测试 SQLModel CRUD 基本功能"""
    app = create_test_app()
    client = TestClient(app)
    
    # 测试 GET 所有 (应该为空)
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == []
    
    # 测试 POST 创建
    product_data = {"name": "笔记本电脑", "price": 5999.0, "stock": 10}
    response = client.post("/products", json=product_data)
    assert response.status_code == 200
    created_product = response.json()
    assert created_product["name"] == "笔记本电脑"
    assert created_product["price"] == 5999.0
    assert created_product["stock"] == 10
    assert "id" in created_product
    product_id = created_product["id"]
    
    # 测试 GET 单个
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == product_id
    assert product["name"] == "笔记本电脑"
    
    # 测试 PUT 更新
    update_data = {"price": 4999.0, "stock": 5}
    response = client.put(f"/products/{product_id}", json=update_data)
    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["price"] == 4999.0
    assert updated_product["stock"] == 5
    assert updated_product["name"] == "笔记本电脑"  # 未更新的字段保持不变
    
    # 测试 DELETE 单个
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    
    # 验证已删除
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404
    
    print("✅ SQLModel CRUD 基本测试通过!")


def test_sqlmodel_pagination():
    """测试 SQLModel 分页功能"""
    app = create_test_app()
    client = TestClient(app)
    
    # 创建多个产品
    for i in range(15):
        client.post("/products", json={
            "name": f"产品{i}",
            "price": i * 100.0,
            "stock": i
        })
    
    # 测试分页
    response = client.get("/products?skip=0&limit=10")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 10
    
    response = client.get("/products?skip=10&limit=10")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 5
    
    # 获取所有
    response = client.get("/products?skip=0&limit=10")
    assert response.status_code == 200
    
    print("✅ SQLModel 分页测试通过!")


def test_sqlmodel_not_found():
    """测试 404 错误"""
    app = create_test_app()
    client = TestClient(app)
    
    # 获取不存在的产品
    response = client.get("/products/999")
    assert response.status_code == 404
    
    # 更新不存在的产品
    response = client.put("/products/999", json={"name": "测试"})
    assert response.status_code == 404
    
    # 删除不存在的产品
    response = client.delete("/products/999")
    assert response.status_code == 404
    
    print("✅ SQLModel 404 测试通过!")


if __name__ == "__main__":
    test_sqlmodel_crud_basic()
    test_sqlmodel_pagination()
    test_sqlmodel_not_found()
    print("\n🎉 所有 SQLModel 测试完成!")

