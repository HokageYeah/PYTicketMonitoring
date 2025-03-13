#!/bin/bash


# 获取脚本所在目录的父目录（即项目根目录）
# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# echo "SCRIPT_DIR: $SCRIPT_DIR"
# PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
# echo "PROJECT_ROOT: $PROJECT_ROOT"
# cd "$PROJECT_ROOT"
# echo "PROJECT_ROOT: $PROJECT_ROOT"

# 必须使用 source 命令执行脚本，这样环境变量才能在当前终端会话中生效。
# 设置环境变量
if [ "$1" = "prod" ] || [ "$1" = "production" ]; then
    export ENV="production"
    ENV_FILE=".env.production"
    DB_ENV_VAR="PROD_DB_NAME"
    echo "已切换到生产环境"
elif [ "$1" = "test" ]; then
    export ENV="test"
    ENV_FILE=".env.test"
    DB_ENV_VAR="TEST_DB_NAME"
    echo "已切换到测试环境"
else
    export ENV="development"
    ENV_FILE=".env.development"
    DB_ENV_VAR="DEV_DB_NAME"
    echo "已切换到开发环境"
fi

# 如果环境特定的 .env 文件存在，则显示相关信息
if [ -f "$ENV_FILE" ]; then
    echo "使用配置文件: $ENV_FILE"
    DB_NAME=$(grep "$DB_ENV_VAR" $ENV_FILE | grep -v "#" | head -1 | cut -d '=' -f2)
    echo "数据库: $DB_NAME"
else
    echo "警告: 环境配置文件 $ENV_FILE 不存在，将使用默认的 .env 文件"
    ENV_FILE=".env"
    # 从默认 .env 文件获取数据库名
    DB_NAME=$(grep "$DB_ENV_VAR" $ENV_FILE | grep -v "#" | head -1 | cut -d '=' -f2)
    echo "数据库: $DB_NAME"
fi

# 显示当前环境
echo "当前环境: $ENV"

# 打印所有参数
echo "所有参数: $@"

# 如果提供了第二个参数，则执行相应的命令
if [ "$2" = "create_db" ] || [ "$2" = "create-db" ]; then
    echo "创建数据库..."
    python src/scripts/manage_db.py create_db
elif [ "$2" = "drop_db" ] || [ "$2" = "drop-db" ]; then
    echo "删除数据库..."
    python src/scripts/manage_db.py drop_db
elif [ "$2" = "create_tables" ] || [ "$2" = "create-tables" ]; then
    echo "创建所有表..."
    python src/scripts/manage_db.py create_tables
elif [ "$2" = "drop_tables" ] || [ "$2" = "drop-tables" ]; then
    echo "删除所有表..."
    python src/scripts/manage_db.py drop_tables
elif [ "$2" = "migrate" ]; then
    if [ -n "$3" ]; then
        # 将所有参数传递给 manage_db.py，从第三个参数开始
        # echo "执行迁移命令: $3 $4 $5 $6 $7..."
        # python src/scripts/manage_db.py migrate $3 $4 $5 $6 $7
        echo "执行迁移命令: ${@:3}"
        python src/scripts/manage_db.py migrate "${@:3}"
    else
        echo "错误: 请提供迁移参数"
        echo "用法: source scripts/set_env.sh [env] migrate [command] [options]"
    fi
elif [ "$2" = "upgrade" ]; then
    echo "应用迁移到最新版本..."
    python src/scripts/manage_db.py upgrade
elif [ "$2" = "downgrade" ]; then
    echo "回滚迁移到上一个版本..."
    python src/scripts/manage_db.py downgrade
elif [ "$2" = "reset" ]; then
    echo "重置数据库..."
    python src/scripts/manage_db.py reset
elif [ "$2" = "history" ]; then
    echo "查看迁移历史..."
    python src/scripts/manage_db.py history
elif [ "$2" = "create-migration" ]; then
    # 如果提供了第三个参数作为迁移名称
    if [ -n "$3" ]; then
        echo "所有参数: $@"
        echo "创建迁移脚本: $3..."
        python src/scripts/manage_db.py migrate revision --autogenerate -m "$3"
    else
        echo "错误: 请提供迁移名称"
        echo "用法: source scripts/set_env.sh [env] create-migration [migration_name]"
    fi
fi