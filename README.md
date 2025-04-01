# 演唱会回流票监控程序

集齐大麦、猫眼、纷玩岛，票星球，4个平台的回流票监控

## 使用

### 一、源代码
```bash
# 克隆本项目
git clone https://github.com/HokageYeah/PYTicketMonitoring
cd TicketMonitoring
# 安装python运行需要的包
python3 -m pip install -r requirements.txt
# 执行程序
python3 main.py
```
程序默认没有用代理，若要添加代理请修改`config.json`(自建隧道代理查看GitHub：[ProxyServer](https://github.com/ThinkerWen/ProxyServer))

### 二、Docker（推荐）
```bash
mkdir /etc/ticket-monitor
vim /etc/ticket-monitor/config.json  # 配置文件见config.json⬆️️
docker run -d --restart=unless-stopped -v /etc/ticket-monitor/config.json:/app/config.json --name="ticket-monitor" designerwang/ticket-monitor:latest
```
<br>

## 添加监控演出

添加新的演出监控请在`TicketMonitoring`文件夹下的`config.json`中配置，

| 字段名       | 含义      | 备注                                                                |
|-----------|---------|-------------------------------------------------------------------|
| show_id   | 演出id    | 通过抓包获取，找到类似于`perfromId` `projectId` `showId` 等的关键字即可              |
| show_name | 演出名称    | 可以任意填写，自己好记即可                                                     |
| platform  | 演出的监控平台 | 和`show_id`的平台对应，`platform`参照：(`大麦: 0` `猫眼: 1` ` 纷玩岛: 2` `票星球: 3`) |
| deadline  | 监控的截止时间 | 截止时间内进行监控，超过截止时间则停止监控,需按照`2000-01-01 00:00:00`格式填写                |


<br>


#### Mac 电脑 如何通过openssl 对nodejs生成公钥和私钥
  
  1、打开终端，输入以下命令来生成私钥：

  ```shell
  genrsa: 生成出来的key是不需要输入密码的。
  
  openssl genrsa -out private_key.pem 2048
  ```
  2、输入以下命令来生成公钥：

  ```shell
  openssl rsa -pubout -in private_key.pem -out public_key.pem
  ```
  在这个过程中，系统将提示您输入密码。如果您需要将密码保护私钥，请输入密码并妥善保管。


#### python项目用到的技术框架
1. fastapi
   说明：fastapi 是一个python的web框架，可以方便的进行web开发
   使用：
   ```python
   from fastapi import FastAPI
   app = FastAPI()
   # 添加路由
   @app.get("/")
   def read_root():
       return {"message": "Hello, World!"}
   # 启动服务
   uvicorn main:app --reload
   ```
2. uvicorn
   说明：uvicorn 是一个python的web框架，可以方便的进行web开发，uvicorn是一个支持异步的asgi服务器，可以方便的进行异步开发
   使用：
   ```python
   uvicorn main:app --reload
   ```
3. sqlalchemy
   说明：sqlalchemy 是python的一个orm框架，可以方便的进行数据库操作
   使用：
   ```python
   from sqlalchemy import create_engine
   from src.config.config import DATABASE_URL
   engine = create_engine(DATABASE_URL)
   # 创建表
   Base.metadata.create_all(engine)
   # 插入数据
   session = Session(engine)
   session.add(User(name="John", email="john@example.com"))
   session.commit()
   ```
4. alembic
   说明：alembic 是sqlalchemy的一个迁移工具，可以方便的进行数据库迁移
   Alembic 命令及其作用：
   ```bash
   # 初始化迁移环境
   alembic init migrations

   # 自动生成迁移脚本
   alembic revision --autogenerate -m "描述信息"
   alembic revision --autogenerate -m "init" / "auto migration"

   # 手动创建一个空的迁移脚本，需要自己编写升级和降级的逻辑。
   alembic revision -m "添加索引"

   # upgrade - 升级数据库到指定版本
   alembic upgrade head  # 升级到最新版本
   alembic upgrade +2    # 升级2个版本
   alembic upgrade 版本号  # 升级到指定版本

   # downgrade - 降级数据库到指定版本
   alembic downgrade base  # 降级到初始状态
   alembic downgrade -1    # 降级1个版本
   alembic downgrade 版本号  # 降级到指定版本

   # history - 查看迁移历史
   alembic history
   alembic history -r版本1:版本2  # 显示指定范围的历史

   # current - 查看当前迁移版本
   alembic current

   # show - 查看迁移脚本
   alembic show

   # heads - 显示最新的迁移版本
   alembic heads

   # branches - 显示分支信息
   alembic branches

   # merge - 合并多个迁移分支
   alembic merge -m "合并分支" 版本1 版本2

   # stamp - 标记数据库版本
   alembic stamp 版本号

   # edit - 编辑指定版本的迁移脚本
   alembic edit 版本号

   ```
   前移脚本在src/scripts/manage_db.py中
5. jwt
   说明：jwt 是json web token，可以方便的进行token认证
   使用：
   ```python
   from jwt import encode, decode
   # 生成token
   token = encode(payload, key, algorithm="HS256")
   # 解码token
   payload = decode(token, key, algorithms=["HS256"])
   ```
6. mysql
   说明：mysql 是数据库，可以方便的进行数据存储
   使用：
   ```python
   from sqlalchemy import create_engine
   from src.config.config import DATABASE_URL
   engine = create_engine(DATABASE_URL)
   ```
7. python-dotenv
   说明：python-dotenv 是一个python的库，可以方便的进行环境变量管理，他可以读取.env文件的环境变量，并设置到环境变量中。配合pydantic-settings库使用，在项目启动的时候，会读取.env文件的环境变量，并设置到pydantic-settings库中
   使用：
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
8. pydantic-settings
   说明：pydantic-settings 是一个python的库，可以方便的进行配置管理
   使用：
   ```python
   from pydantic_settings import BaseSettings
   class Settings(BaseSettings):
       # 配置字段
       ...
   settings = Settings()
   ```
9.  pydantic
   说明：pydantic 是一个python的库，可以方便的进行数据验证
   使用：
   ```python
   from pydantic import BaseModel
   class User(BaseModel):
       id: int
       name: str
   ```
10. cachetools
   说明：cachetools 是一个python的库，可以方便的进行缓存管理，可以减少数据库查询，提高接口响应速度。
   使用：
   ```python
   from cachetools import TTLCache
   cache = TTLCache(maxsize=1000, ttl=60)
   cache['key'] = 'value'
   ```
11. fastapi-mail
   说明：fastapi-mail 是一个fastapi的邮件发送库，可以方便的进行邮件发送
   使用 fastapi-mail 库相比原始的 smtplib 实现有以下优势：
    * 1. 异步支持 ：原生支持 FastAPI 的异步特性，提高系统性能
    * 2. 简化代码 ：大幅减少了代码量，更加简洁易读
    * 3. 更好的错误处理 ：提供了更完善的错误处理机制
    * 4. 模板支持 ：支持 Jinja2 模板，可以更方便地创建复杂邮件
    * 5. 附件支持 ：简化了附件的处理流程
    * 6. 批量发送 ：更容易实现批量邮件发送
    * 7. 类型提示 ：完整的类型提示，提高代码可维护性
   使用：
   ```python
   from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
   ```
12. httpx
    说明：httpx 是一个python的库，可以方便的进行http请求
    使用：
    ```python
    import httpx
    response = httpx.get('https://api.github.com')
    print(response.text)
    ```
13. uvloop
    说明：uvloop 是一个python的库，可以方便的进行异步io操作（异步io操作可以提高程序的性能）推荐使用，项目中暂未替换
    ```python
      import asyncio
      import uvloop
      asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
      # 编写asyncio的代码，与之前写的代码一致。
      # 内部的事件循环自动化会变为uvloop
      asyncio.run(...)
    ```

#### python项目转换为 HTTPS
首先，你需要获取 SSL 证书。有几种方式：
- 使用自签名证书（开发环境）
- 使用 Let's Encrypt 等免费证书（生产环境）
- 购买商业 SSL 证书

> 这里使用自签名证书（开发环境）
1. 创建一个目录用于存放证书和密钥
```bash
mkdir -p /Users/yuye/YeahWork/小项目/演唱会回流票监控程序/PYTicketMonitoring/ssl
cd /Users/yuye/YeahWork/小项目/演唱会回流票监控程序/PYTicketMonitoring/ssl
```
2. 生成证书和密钥
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```
3. 配置 fastapi 使用 SSL 证书(settings 中添加 SSL 相关配置)
```python
# core/config.py 添加 SSL 配置
SSL_KEYFILE = os.getenv("SSL_KEYFILE", "/Users/yuye/YeahWork/小项目/演唱会回流票监控程序/PYTicketMonitoring/ssl/key.pem")
SSL_CERTFILE = os.getenv("SSL_CERTFILE", "/Users/yuye/YeahWork/小项目/演唱会回流票监控程序/PYTicketMonitoring/ssl/cert.pem")
USE_HTTPS = os.getenv("USE_HTTPS", "True").lower() in ("true", "1", "t")
```
```bash
# 然后在 main.py 中使用这些配置
if __name__ == "__main__":
    uvicorn_config = {
        'app': 'main:app',
        'host': "0.0.0.0",
        'port': 8001,
        'reload': True
    }
    
    if settings.USE_HTTPS:
        uvicorn_config.update({
            'ssl_keyfile': settings.SSL_KEYFILE,
            'ssl_certfile': settings.SSL_CERTFILE
        })
    
    uvicorn.run(**uvicorn_config)
```

#### set_env.sh 脚本的执行（废弃方案，此方法只能在当前shell环境下改变环境变量，当shell执行完毕，在运行起项目的时候，环境变量会恢复到原来的状态）

```bash
# Mac电脑更改环境需要执行 source
# 切换到开发环境并创建数据库
source scripts/set_env.sh dev create_db

# 切换到测试环境并创建所有表
source scripts/set_env.sh test create_tables

# 切换到生产环境并应用迁移
source scripts/set_env.sh prod upgrade

# 切换到开发环境并回滚迁移
source scripts/set_env.sh dev downgrade

# 切换到测试环境并重置数据库
source scripts/set_env.sh test reset

# 切换到开发环境并创建迁移脚本
source scripts/set_env.sh dev create-migration "add_new_table"

# 切换到开发环境并查看迁移历史
source scripts/set_env.sh dev history

# 切换到开发环境并执行自定义迁移命令
source scripts/set_env.sh dev migrate revision --autogenerate -m "create_new_table"

# 查看当前迁移版本
source scripts/set_env.sh dev current

# 指定迁移版本
source scripts/set_env.sh dev upgrade ebc3134199c9

# 添加索引或修改数据
source scripts/set_env.sh dev migrate revision -m "添加索引"
# 手动添加表
alembic revision -m "insert_initial_users"
```

#### set_env.py执行 使用dotenv库启动指定环境（推荐方案）

> 注意：
> 1、环境变量的优先级：系统环境变量 > .env.local > .env > pydantic 默认值

* 1、先通过dotenv库设置.env的文件环境，在读取.env文件的环境变量
```bash
# 第一步 运行脚本设置环境
python src/scripts/set_env.py test

# 第二步 启动服务
python main.py 或者 uvicorn main:app --reload --port 8001
```

* 2、不设置.env文件环境，直接通过dotenv库启动的时候读取特定文件如（.env.test、.env.production等）文件的环境变量
```bash
# Linux/Mac
APP_ENV=prod uvicorn app.main:app --reload --port 8001
# Windows (PowerShell)
$env:APP_ENV="prod"; uvicorn app.main:app --reload --port 8001
```

#### docker部署上线
<!-- 使用docker compose部署上线 -->
*  使用docker compose部署上线，需要先安装docker compose，然后使用docker compose up -d --build命令启动服务。
*  docker镜像中初始化数据库：
   * 确保容器启动时自动创建表结构，已经修改 Dockerfile 文件，在容器启动时执行 python src/scripts/docker-entrypoint.sh自动化在容器启动时创建数据库表
   * 如果上述失败的平替方案：
     * 方案一：创建数据库mysql，并设置环境变量MYSQL_ROOT_PASSWORD=aa123456，MYSQL_USER=yy，MYSQL_PASSWORD=aa123456，MYSQL_DATABASE=ticket_monitor_db_prod
     * 方案二：进入容器 docker exec -it ticket_monitor bash，然后执行python /app/src/scripts/set_env.py prod upgrade（alembic upgrade head）命令更新表。如果表不存在运行python src/scripts/set_env.py prod  migrate revision --autogenerate -m "pro_table"  创建表
     * 方案三：docker exec -it ticket_monitor python /app/src/scripts/docker_init_db.py
```bash
# 构建镜像
docker compose build
# 启动服务 合并构建和启动 docker compose up -d --build
docker compose up -d
# 停止服务
docker compose down
# 查看日志
docker compose logs -f
# 进入容器
docker compose exec ticket-monitor bash
```




# 注意

程序仅供学习，请勿用于违法活动中，如作他用所承受的法律责任一概与作者无关

编程能力蒟蒻，代码仅供参考^_^

----

原文链接：<a href="https://bbs.kanxue.com/thread-279165.htm">[看雪] 某麦网回流票监控，sing参数分析</a>

原文链接：<a href="https://www.52pojie.cn/forum.php?mod=viewthread&tid=1845064&extra=page%3D1%26filter%3Dtypeid%26typeid%3D378">[吾爱破解] 某麦网回流票监控，sing参数分析</a>
