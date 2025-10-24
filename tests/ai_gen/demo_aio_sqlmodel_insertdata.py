"""使用异步 SQLModel 插入测试数据"""

import asyncio
import random
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from tests.ai_gen.demo_aio_sqlmodel import Book


# 图书标题列表
BOOK_TITLES = [
    "Python编程入门", "数据结构与算法", "机器学习实战", "深度学习原理", 
    "Web开发指南", "数据库系统概念", "操作系统原理", "计算机网络",
    "软件工程实践", "人工智能导论", "Java核心技术", "C++程序设计",
    "JavaScript权威指南", "React开发实战", "Vue.js从入门到精通", 
    "Docker容器技术", "Kubernetes实战", "微服务架构设计", "DevOps实践",
    "敏捷开发方法"
]

# 作者列表
AUTHORS = [
    "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
    "郑一", "王二", "冯三", "陈四", "褚五", "卫六", "蒋七", "沈八",
    "韩九", "杨十", "朱一", "秦二"
]

def generate_isbn():
    """生成一个模拟的ISBN号码"""
    parts = [
        "978",
        str(random.randint(0, 999)).zfill(3),
        str(random.randint(0, 9999)).zfill(4),
        str(random.randint(0, 9999)).zfill(4),
        str(random.randint(0, 9))
    ]
    return "-".join(parts)

def generate_price():
    """生成一个随机价格"""
    return round(random.uniform(20, 150), 2)

async def insert_test_data():
    """插入测试数据"""
    # 创建数据库引擎
    DATABASE_URL = "sqlite+aiosqlite:///./test_aio_sqlmodel.db"
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # 插入100条测试数据
    async with AsyncSession(engine) as session:
        for i in range(100):
            # 随机选择标题和作者
            title = random.choice(BOOK_TITLES) + f" 第{random.randint(1, 5)}版"
            author = random.choice(AUTHORS)
            price = generate_price()
            isbn = generate_isbn()
            
            # 确保ISBN唯一
            while True:
                try:
                    # 创建图书对象
                    book = Book(
                        title=title,
                        author=author,
                        price=price,
                        isbn=isbn
                    )
                    session.add(book)
                    await session.commit()
                    await session.refresh(book)
                    break
                except Exception:
                    # 如果ISBN重复，重新生成
                    await session.rollback()
                    isbn = generate_isbn()
            
            # 每10条记录显示一次进度
            if (i + 1) % 10 == 0:
                print(f"已插入 {i + 1} 条记录")
    
    print("数据插入完成，共插入 100 条记录")

if __name__ == "__main__":
    asyncio.run(insert_test_data())