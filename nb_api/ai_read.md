nb_api 是一个框架, 用户在定义orm后,使用nb_api 自动生成接口,用户少写简单代码

1.使用最新版本的 fastapi + pydantic v2 ,开发 nb_api
2.nb_api 要实现 三方包 fastapi_crudrouter 的所有功能和接口,教程和源码在 tests/fastapi_crudrouter_all_docs_and_codes.md
3.nb_api 只需要兼容sqlmodel,不需要兼容 tortoise ormar sqlchemy 等orm
4.python版本要求python3.9以上
5.框架代码写在 nb_api 文件夹下
6.ai验证代码时候要使用python 解释器 D:/ProgramData/Miniconda3/envs/py39b/python.exe

我现在需要开发一个nb_api的三方包,实现上面的功能,你来帮我实现