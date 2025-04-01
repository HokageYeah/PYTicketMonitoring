#!/bin/bash
set -e
# 脚本以`set -e`开头，这意味着脚本会在任何命令返回非零状态时立即退出

# 等待 MySQL 准备就绪
echo "等待 MySQL 准备就绪..."
until python -c "import mysql.connector; mysql.connector.connect(host='mysql', user='root', password='aa123456')" &> /dev/null
do
  echo "MySQL 尚未准备就绪 - 等待..."
  sleep 3
done
echo "MySQL 已准备就绪"

# 创建数据库（如果不存在）
# ，`||`是bash中的逻辑或操作符。如果左边的命令（即`python src/scripts/set_env.py prod create_db`）执行失败（返回非零状态码），右边的命令`true`就会执行。`true`是一个总是返回成功（0）的命令。因此，这行代码的作用是即使创建数据库的命令失败，脚本也不会因为`set -e`而退出，而是继续执行后面的步骤。
python src/scripts/set_env.py prod create_db || true

# 初始化数据库
python src/scripts/docker_init_db.py || true

# 创建最新的指向
python src/scripts/set_env.py prod migrate revision --autogenerate -m "pro_table" || true

# 执行数据库迁移
echo "执行数据库迁移..."
python src/scripts/set_env.py prod upgrade || python src/scripts/docker_init_db.py

# 执行原始命令
exec "$@"