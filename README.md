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
python3 start.py
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
2. sqlalchemy
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
3. alembic
   说明：alembic 是sqlalchemy的一个迁移工具，可以方便的进行数据库迁移
   使用：
   ```bash
   # 初始化迁移环境
   alembic init migrations
   # 生成迁移脚本
   alembic revision --autogenerate -m "init"
   # 应用迁移脚本
   alembic upgrade head
   # 回滚迁移脚本
   alembic downgrade -1
   # 查看迁移历史
   alembic history
   # 查看迁移脚本
   alembic show
   ```
   前移脚本在src/scripts/manage_db.py中
4. jwt
   说明：jwt 是json web token，可以方便的进行token认证
   使用：
   ```python
   from jwt import encode, decode
   # 生成token
   token = encode(payload, key, algorithm="HS256")
   # 解码token
   payload = decode(token, key, algorithms=["HS256"])
   ```
5. mysql
   说明：mysql 是数据库，可以方便的进行数据存储
   使用：
   ```python
   from sqlalchemy import create_engine
   from src.config.config import DATABASE_URL
   engine = create_engine(DATABASE_URL)
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

# 注意

程序仅供学习，请勿用于违法活动中，如作他用所承受的法律责任一概与作者无关

编程能力蒟蒻，代码仅供参考^_^

----

原文链接：<a href="https://bbs.kanxue.com/thread-279165.htm">[看雪] 某麦网回流票监控，sing参数分析</a>

原文链接：<a href="https://www.52pojie.cn/forum.php?mod=viewthread&tid=1845064&extra=page%3D1%26filter%3Dtypeid%26typeid%3D378">[吾爱破解] 某麦网回流票监控，sing参数分析</a>
