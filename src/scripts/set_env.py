import os
import sys
import subprocess

def set_project_env(env_type):
    # 设置基本环境变量
    if env_type in ["prod", "production"]:
        os.environ["ENV"] = "production"
        env_file = ".env.production"
        db_env_var = "PROD_DB_NAME"
        print("已切换到生产环境")
    elif env_type == "test":
        os.environ["ENV"] = "test"
        env_file = ".env.test"
        db_env_var = "TEST_DB_NAME"
        print("已切换到测试环境")
    else:
        os.environ["ENV"] = "development"
        env_file = ".env.development"
        db_env_var = "DEV_DB_NAME"
        print("已切换到开发环境")

    print(f"当前环境: {os.environ['ENV']}")  # 添加调试信息

    # 检查环境文件是否存在
    if os.path.isfile(env_file):
        print(f"使用配置文件: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('#') and line.strip():
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"设置环境变量: {key.strip()} = {value.strip()}")
        
        # 获取并显示数据库名称
        db_name = os.getenv(db_env_var)  # 使用 db_env_var 变量
        print(f"数据库1: {db_name}")
    else:
        print(f"警告: 环境配置文件 {env_file} 不存在，将使用默认的 .env 文件")
        env_file = ".env"
        if os.path.isfile(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.startswith('#') and line.strip():
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        else:
            print("错误: 找不到任何环境配置文件")
            sys.exit(1)
# 使用 sys.executable 来确保使用当前 Python 环境的解释器，而不需要激活虚拟环境
def invoke_database_command(command, additional_args):
    print(f"Command: {command}")

    if command in ["create_db", "create-db"]:
        print("创建数据库...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "create_db"])
    elif command in ["drop_db", "drop-db"]:
        print("删除数据库...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "drop_db"])
    elif command in ["create_tables", "create-tables"]:
        print("创建所有表...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "create_tables"])
    elif command in ["drop_tables", "drop-tables"]:
        print("删除所有表...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "drop_tables"])
    elif command == "migrate":
        if additional_args:
            print(f"执行迁移命令: {' '.join(additional_args)}")
            subprocess.run([sys.executable, "src/scripts/manage_db.py", "migrate"] + additional_args)
        else:
            print("错误: 请提供迁移参数")
            print("用法: python set_env.py [env] migrate [command] [options]")
    elif command == "upgrade":
        print("应用迁移到最新版本...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "upgrade"])
    elif command == "downgrade":
        print("回滚迁移到上一个版本...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "downgrade"])
    elif command == "reset":
        print("重置数据库...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "reset"])
    elif command == "history":
        print("查看迁移历史...")
        subprocess.run([sys.executable, "src/scripts/manage_db.py", "history"])
    elif command == "create-migration":
        if additional_args:
            print(f"创建迁移脚本: {additional_args[0]}...")
            subprocess.run([sys.executable, "src/scripts/manage_db.py", "migrate", "revision", "--autogenerate", "-m", additional_args[0]])
        else:
            print("错误: 请提供迁移名称")
            print("用法: python set_env.py [env] create-migration [migration_name]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python set_env.py [env] [command] [options]")
        sys.exit(1)

    env_type = sys.argv[1]
    set_project_env(env_type)

    if len(sys.argv) > 2:
        command = sys.argv[2]
        additional_args = sys.argv[3:]
        invoke_database_command(command, additional_args)

    # 显示当前环境信息
    print("\n当前环境信息:")
    print("----------------------------------------")
    print(f"环境类型: {os.getenv('ENV')}")
    print(f"数据库2: {os.getenv('DB_ENV_VAR')}")
    print("----------------------------------------")