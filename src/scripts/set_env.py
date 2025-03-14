# import os
# import sys
# import subprocess

# def set_project_env(env_type):
#     # 设置基本环境变量
#     if env_type in ["prod", "production"]:
#         os.environ["ENV"] = "production"
#         env_file = ".env.production"
#         db_env_var = "DB_NAME"
#         print("已切换到生产环境")
#     elif env_type == "test":
#         os.environ["ENV"] = "test"
#         env_file = ".env.test"
#         db_env_var = "DB_NAME"
#         print("已切换到测试环境")
#     else:
#         os.environ["ENV"] = "development"
#         env_file = ".env.development"
#         db_env_var = "DB_NAME"
#         print("已切换到开发环境")

#     print(f"当前环境: {os.environ['ENV']}")  # 添加调试信息

#     # 检查环境文件是否存在
#     if os.path.isfile(env_file):
#         print(f"使用配置文件: {env_file}")
#         with open(env_file, 'r', encoding='utf-8') as f:
#             for line in f:
#                 if not line.startswith('#') and line.strip():
#                     key, value = line.split('=', 1)
#                     os.environ[key.strip()] = value.strip()
#                     print(f"设置环境变量: {key.strip()} = {value.strip()}")
        
#         # 获取并显示数据库名称
#         db_name = os.getenv(db_env_var)  # 使用 db_env_var 变量
#         print(f"数据库1: {db_name}")
#     else:
#         print(f"警告: 环境配置文件 {env_file} 不存在，将使用默认的 .env 文件")
#         env_file = ".env"
#         if os.path.isfile(env_file):
#             with open(env_file, 'r', encoding='utf-8') as f:
#                 for line in f:
#                     if not line.startswith('#') and line.strip():
#                         key, value = line.split('=', 1)
#                         os.environ[key.strip()] = value.strip()
#         else:
#             print("错误: 找不到任何环境配置文件")
#             sys.exit(1)
# # 使用 sys.executable 来确保使用当前 Python 环境的解释器，而不需要激活虚拟环境
# def invoke_database_command(command, additional_args):
#     print(f"Command: {command}")

#     if command in ["create_db", "create-db"]:
#         print("创建数据库...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "create_db"])
#     elif command in ["drop_db", "drop-db"]:
#         print("删除数据库...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "drop_db"])
#     elif command in ["create_tables", "create-tables"]:
#         print("创建所有表...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "create_tables"])
#     elif command in ["drop_tables", "drop-tables"]:
#         print("删除所有表...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "drop_tables"])
#     elif command == "migrate":
#         if additional_args:
#             print(f"执行迁移命令: {' '.join(additional_args)}")
#             subprocess.run([sys.executable, "src/scripts/manage_db.py", "migrate"] + additional_args)
#         else:
#             print("错误: 请提供迁移参数")
#             print("用法: python set_env.py [env] migrate [command] [options]")
#     elif command == "upgrade":
#         print("应用迁移到最新版本...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "upgrade"])
#     elif command == "downgrade":
#         print("回滚迁移到上一个版本...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "downgrade"])
#     elif command == "reset":
#         print("重置数据库...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "reset"])
#     elif command == "history":
#         print("查看迁移历史...")
#         subprocess.run([sys.executable, "src/scripts/manage_db.py", "history"])
#     elif command == "create-migration":
#         if additional_args:
#             print(f"创建迁移脚本: {additional_args[0]}...")
#             subprocess.run([sys.executable, "src/scripts/manage_db.py", "migrate", "revision", "--autogenerate", "-m", additional_args[0]])
#         else:
#             print("错误: 请提供迁移名称")
#             print("用法: python set_env.py [env] create-migration [migration_name]")

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("用法: python set_env.py [env] [command] [options]")
#         sys.exit(1)

#     env_type = sys.argv[1]
#     set_project_env(env_type)

#     if len(sys.argv) > 2:
#         command = sys.argv[2]
#         additional_args = sys.argv[3:]
#         invoke_database_command(command, additional_args)

#     # 显示当前环境信息
#     print("\n当前环境信息:")
#     print("----------------------------------------")
#     print(f"环境类型: {os.getenv('ENV')}")
#     print(f"数据库2: {os.getenv('DB_ENV_VAR')}")
#     print("----------------------------------------")




# import os
# import sys
# import subprocess
# import platform

# def set_project_env(env_type):
#     # 设置基本环境变量
#     if env_type in ["prod", "production"]:
#         os.environ["ENV"] = "production"
#         env_file = ".env.production"
#         db_env_var = "DB_NAME"
#         print("已切换到生产环境")
#     elif env_type == "test":
#         os.environ["ENV"] = "test"
#         env_file = ".env.test"
#         db_env_var = "DB_NAME"
#         print("已切换到测试环境")
#     else:
#         os.environ["ENV"] = "development"
#         env_file = ".env.development"
#         db_env_var = "DB_NAME"
#         print("已切换到开发环境")

#     print(f"当前环境: {os.environ['ENV']}")  # 添加调试信息

#     # 检查环境文件是否存在
#     if os.path.isfile(env_file):
#         print(f"使用配置文件: {env_file}")
#         with open(env_file, 'r', encoding='utf-8') as f:
#             for line in f:
#                 if not line.startswith('#') and line.strip():
#                     try:
#                         key, value = line.split('=', 1)
#                         os.environ[key.strip()] = value.strip()
#                         print(f"设置环境变量: {key.strip()} = {value.strip()}")
#                     except ValueError:
#                         print(f"警告: 无法解析行: {line.strip()}")
        
#         # 获取并显示数据库名称
#         db_name = os.getenv(db_env_var)  # 使用 db_env_var 变量
#         print(f"数据库1: {db_name}")
#     else:
#         print(f"警告: 环境配置文件 {env_file} 不存在，将使用默认的 .env 文件")
#         env_file = ".env"
#         if os.path.isfile(env_file):
#             with open(env_file, 'r', encoding='utf-8') as f:
#                 for line in f:
#                     if not line.startswith('#') and line.strip():
#                         try:
#                             key, value = line.split('=', 1)
#                             os.environ[key.strip()] = value.strip()
#                         except ValueError:
#                             print(f"警告: 无法解析行: {line.strip()}")
#         else:
#             print("错误: 找不到任何环境配置文件")
#             sys.exit(1)
    
#     # 保存环境变量到 DB_ENV_VAR
#     os.environ["DB_ENV_VAR"] = db_env_var

# # 使用 sys.executable 来确保使用当前 Python 环境的解释器，而不需要激活虚拟环境
# def invoke_database_command(command, additional_args):
#     print(f"Command: {command}")
    
#     # 创建环境变量副本，确保子进程能够继承当前进程的环境变量
#     env = os.environ.copy()
    
#     # 检测操作系统类型
#     is_windows = platform.system() == "Windows"
#     script_path = "src\\scripts\\manage_db.py" if is_windows else "src/scripts/manage_db.py"
    
#     # 在 Windows 上使用 shell=True 可以帮助环境变量传递
#     shell_option = is_windows

#     if command in ["create_db", "create-db"]:
#         print("创建数据库...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} create_db"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "create_db"], env=env)
#     elif command in ["drop_db", "drop-db"]:
#         print("删除数据库...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} drop_db"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "drop_db"], env=env)
#     elif command in ["create_tables", "create-tables"]:
#         print("创建所有表...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} create_tables"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "create_tables"], env=env)
#     elif command in ["drop_tables", "drop-tables"]:
#         print("删除所有表...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} drop_tables"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "drop_tables"], env=env)
#     elif command == "migrate":
#         if additional_args:
#             print(f"执行迁移命令: {' '.join(additional_args)}")
#             if is_windows:
#                 cmd = f"{sys.executable} {script_path} migrate {' '.join(additional_args)}"
#                 subprocess.run(cmd, env=env, shell=True)
#             else:
#                 subprocess.run([sys.executable, script_path, "migrate"] + additional_args, env=env)
#         else:
#             print("错误: 请提供迁移参数")
#             print("用法: python set_env.py [env] migrate [command] [options]")
#     elif command == "upgrade":
#         print("应用迁移到最新版本...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} upgrade"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "upgrade"], env=env)
#     elif command == "downgrade":
#         print("回滚迁移到上一个版本...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} downgrade"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "downgrade"], env=env)
#     elif command == "reset":
#         print("重置数据库...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} reset"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "reset"], env=env)
#     elif command == "history":
#         print("查看迁移历史...")
#         if is_windows:
#             cmd = f"{sys.executable} {script_path} history"
#             subprocess.run(cmd, env=env, shell=True)
#         else:
#             subprocess.run([sys.executable, script_path, "history"], env=env)
#     elif command == "create-migration":
#         if additional_args:
#             print(f"创建迁移脚本: {additional_args[0]}...")
#             if is_windows:
#                 cmd = f"{sys.executable} {script_path} migrate revision --autogenerate -m \"{additional_args[0]}\""
#                 subprocess.run(cmd, env=env, shell=True)
#             else:
#                 subprocess.run([sys.executable, script_path, "migrate", "revision", "--autogenerate", "-m", additional_args[0]], env=env)
#         else:
#             print("错误: 请提供迁移名称")
#             print("用法: python set_env.py [env] create-migration [migration_name]")

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("用法: python set_env.py [env] [command] [options]")
#         sys.exit(1)

#     env_type = sys.argv[1]
#     set_project_env(env_type)

#     if len(sys.argv) > 2:
#         command = sys.argv[2]
#         additional_args = sys.argv[3:]
#         invoke_database_command(command, additional_args)

#     # 显示当前环境信息
#     print("\n当前环境信息:")
#     print("----------------------------------------")
#     print(f"环境类型: {os.getenv('ENV', 'none')}")  # 添加默认值'none'以便于调试
#     print(f"数据库2: {os.getenv('DB_NAME', 'none')}")  # 添加默认值'none'以便于调试
#     print("----------------------------------------")







import os
import sys
import subprocess
import platform
from dotenv import load_dotenv, set_key, find_dotenv

def set_project_env(env_type):
    # 设置基本环境变量
    if env_type in ["prod", "production"]:
        env_value = "production"
        env_file = ".env.production"
        db_env_var = "DB_NAME"
        print("已切换到生产环境")
    elif env_type == "test":
        env_value = "test"
        env_file = ".env.test"
        db_env_var = "DB_NAME"
        print("已切换到测试环境")
    else:
        env_value = "development"
        env_file = ".env.development"
        db_env_var = "DB_NAME"
        print("已切换到开发环境")
    
    # 设置环境变量
    os.environ["ENV"] = env_value
    print(f"当前环境: {os.environ['ENV']}")  # 添加调试信息

    # 创建或更新 .env 文件
    dotenv_path = find_dotenv(usecwd=True) or ".env"
    if not os.path.exists(dotenv_path):
        # 如果 .env 文件不存在，创建一个空文件
        with open(dotenv_path, "w") as f:
            pass
    
    # 将环境类型写入 .env 文件
    set_key(dotenv_path, "ENV", env_value)
    print(f"已将环境类型 {env_value} 写入 {dotenv_path} 文件")

    # 检查环境文件是否存在
    if os.path.isfile(env_file):
        print(f"使用配置文件: {env_file}")
        # 加载特定环境的配置文件
        load_dotenv(env_file, override=True)
        # 将特定环境的配置写入 .env 文件
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('#') and line.strip():
                    try:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 使用 set_key 将变量写入 .env 文件
                        set_key(dotenv_path, key, value)
                        print(f"设置环境变量: {key} = {value}")
                    except ValueError:
                        print(f"警告: 无法解析行: {line.strip()}")
        
        # 获取并显示数据库名称
        db_name = os.getenv(db_env_var)  # 使用 db_env_var 变量
        print(f"数据库1: {db_name}")
    else:
        print(f"警告: 环境配置文件 {env_file} 不存在，将使用默认的 .env 文件")
        env_file = ".env"
        if os.path.isfile(env_file):
            load_dotenv(env_file, override=True)
        else:
            print("错误: 找不到任何环境配置文件")
            sys.exit(1)
    
    # 保存环境变量到 DB_ENV_VAR
    os.environ["DB_ENV_VAR"] = db_env_var

# 使用 sys.executable 来确保使用当前 Python 环境的解释器，而不需要激活虚拟环境
def invoke_database_command(command, additional_args):
    print(f"Command: {command}")
    
    # 创建环境变量副本，确保子进程能够继承当前进程的环境变量
    env = os.environ.copy()
    
    # 检测操作系统类型
    is_windows = platform.system() == "Windows"
    script_path = "src\\scripts\\manage_db.py" if is_windows else "src/scripts/manage_db.py"
    
    # 在 Windows 上使用 shell=True 可以帮助环境变量传递
    shell_option = is_windows

    if command in ["create_db", "create-db"]:
        print("创建数据库...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} create_db"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "create_db"], env=env)
    elif command in ["drop_db", "drop-db"]:
        print("删除数据库...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} drop_db"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "drop_db"], env=env)
    elif command in ["create_tables", "create-tables"]:
        print("创建所有表...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} create_tables"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "create_tables"], env=env)
    elif command in ["drop_tables", "drop-tables"]:
        print("删除所有表...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} drop_tables"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "drop_tables"], env=env)
    elif command == "migrate":
        if additional_args:
            print(f"执行迁移命令: {' '.join(additional_args)}")
            if is_windows:
                cmd = f"{sys.executable} {script_path} migrate {' '.join(additional_args)}"
                subprocess.run(cmd, env=env, shell=True)
            else:
                subprocess.run([sys.executable, script_path, "migrate"] + additional_args, env=env)
        else:
            print("错误: 请提供迁移参数")
            print("用法: python set_env.py [env] migrate [command] [options]")
    elif command == "upgrade":
        print("应用迁移到最新版本...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} upgrade"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "upgrade"], env=env)
    elif command == "downgrade":
        print("回滚迁移到上一个版本...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} downgrade"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "downgrade"], env=env)
    elif command == "reset":
        print("重置数据库...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} reset"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "reset"], env=env)
    elif command == "history":
        print("查看迁移历史...")
        if is_windows:
            cmd = f"{sys.executable} {script_path} history"
            subprocess.run(cmd, env=env, shell=True)
        else:
            subprocess.run([sys.executable, script_path, "history"], env=env)
    elif command == "create-migration":
        if additional_args:
            print(f"创建迁移脚本: {additional_args[0]}...")
            if is_windows:
                cmd = f"{sys.executable} {script_path} migrate revision --autogenerate -m \"{additional_args[0]}\""
                subprocess.run(cmd, env=env, shell=True)
            else:
                subprocess.run([sys.executable, script_path, "migrate", "revision", "--autogenerate", "-m", additional_args[0]], env=env)
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
    print(f"环境类型: {os.getenv('ENV', 'none')}")  # 添加默认值'none'以便于调试
    print(f"数据库2: {os.getenv('DB_NAME', 'none')}")  # 添加默认值'none'以便于调试
    print("----------------------------------------")