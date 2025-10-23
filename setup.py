"""nb_api 安装配置"""

from setuptools import setup, find_packages
from pathlib import Path



# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="very_nb_api",
    version='0.5',
    author="NB API Team",
    author_email="ydf0509@example.com",
    description="基于 FastAPI + Pydantic v2 + SQLModel 的自动 CRUD 路由生成框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/nb_api",
    packages=find_packages(exclude=("tests", "tests.*")),
    package_data={
        "nb_api": ["py.typed"],
    },
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.110.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "sqlmodel": ["sqlmodel>=0.0.14"],
        "dev": [
            "pytest>=7.4.0",
            "httpx>=0.26.0",
            "uvicorn[standard]>=0.27.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",

        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Code Generators",
        "Typing :: Typed",
    ],
    keywords="fastapi crud rest api sqlmodel pydantic router",
)
