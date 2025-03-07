from pathlib import Path
from src.server import untiles
from src import monitor
# 获取src目录的路径
src_path = Path(monitor.__file__).resolve().parent
# 获取db_config.json文件的路径
db_config_path = src_path / 'config' / 'db_config.json'
# 获取untiles目录的路径
untiles_path = Path(untiles.__file__).resolve().parent
# 获取private_key.pem文件的路径
private_key_path = src_path.parent / 'jwt-keys' / 'private_key.pem'
# 获取public_key.pem文件的路径
public_key_path = src_path.parent / 'jwt-keys' / 'public_key.pem'

