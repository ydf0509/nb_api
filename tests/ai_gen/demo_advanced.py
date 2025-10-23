"""高级用法示例 - 自定义路由和依赖注入"""

from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from nb_api import SQLModelCRUDRouter


# 定义模型
class User(SQLModel, table=True):
    """用户模型"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    is_active: bool = Field(default=True)


class UserRead(SQLModel):
    """用户读取模型"""
    id: int
    username: str
    email: str
    is_active: bool


class UserCreate(SQLModel):
    """用户创建模型"""
    username: str
    email: str


class UserUpdate(SQLModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


# 数据库设置
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# 创建 FastAPI 应用
app = FastAPI(title="高级 CRUD 示例")


@app.on_event("startup")
def on_startup():
    init_db()


# 安全认证
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证 Token"""
    if credentials.credentials != "my-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    return credentials.credentials


# 创建带认证的 CRUD 路由
user_router = SQLModelCRUDRouter(
    schema=UserRead,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    db_model=User,
    db=get_session,
    prefix="users",
    tags=["用户管理"],
    paginate=50,
    # 为特定路由添加依赖
    delete_all_route=[Depends(verify_token)],  # 删除所有需要认证
    delete_one_route=[Depends(verify_token)],  # 删除单个需要认证
)


# 自定义路由覆盖
@user_router.get("/{item_id}")
def get_user_custom(item_id: int, db: Session = Depends(get_session)):
    """自定义的获取用户路由"""
    user = db.get(User, item_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    
    # 添加自定义逻辑
    if not user.is_active:
        raise HTTPException(403, "用户已被禁用")
    
    return user


# 添加额外的自定义路由
@user_router.post("/{item_id}/activate")
def activate_user(item_id: int, db: Session = Depends(get_session)):
    """激活用户"""
    user = db.get(User, item_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    
    user.is_active = True
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": f"用户 {user.username} 已激活", "user": user}


@user_router.post("/{item_id}/deactivate")
def deactivate_user(
    item_id: int, 
    db: Session = Depends(get_session),
    token: str = Depends(verify_token)
):
    """停用用户 (需要认证)"""
    user = db.get(User, item_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": f"用户 {user.username} 已停用", "user": user}


# 注册路由
app.include_router(user_router)


if __name__ == "__main__":
    import uvicorn
    
    print("启动服务器...")
    print("API 文档: http://127.0.0.1:8000/docs")
    print("\n使用 Bearer Token 'my-secret-token' 进行认证")
    uvicorn.run(app, host="127.0.0.1", port=8000)

