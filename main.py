import json
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
# current_dir = Path(__file__).resolve().parent
# src_dir = current_dir / 'src'
# sys.path.append(str(src_dir))

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)


def main():
    try:
        # 导入并使用 OpenBrowerGetCookie
        from src.browser.openBrowerGetCookie import open_browser_get_cookie
        
        print("正在启动浏览器...")
        cookie_info = open_browser_get_cookie()
        # 判断cookie_info对象有没有指
        if len(cookie_info) > 0:
            # 格式化cookie
            formatted_cookies = cookie_info
            # 初始化配置
            config = {}
            print("成功获取Cookie信息---cookie_info---", cookie_info)
            print("成功获取Cookie信息---formatted_cookies---", formatted_cookies)
            # 这里可以添加后续的处理逻辑
            current_dir = Path(__file__).resolve().parent / 'src' / 'monitor' / 'cookies'
            # 如果文件存在，则读取文件
            if os.path.exists(current_dir / "cookies.json"):
                try:
                    with open(current_dir / "cookies.json", "r", encoding="utf-8") as file:
                        config = json.load(file)
                        config['cookie'] = formatted_cookies
                except Exception as e:
                    print(f"读取cookies.json文件失败: {e}")
            else:
                config['cookie'] = formatted_cookies
            with open(current_dir / "cookies.json", "w", encoding="utf-8") as file:
                json.dump(config, file, ensure_ascii=False, indent=2)
            print("Cookie保存成功")
        else:
            print("获取Cookie失败")
            
    except Exception as e:
        print(f"程序运行出错: {e}")
        return 1
    
    return 0

# 大麦登录
def login_dm():
    from src.simulateLogin.Login_DM import Login_DM
    login_dm = Login_DM()
    print('login_dm----', login_dm)

if __name__ == "__main__":
    # exit_code = main()
    # sys.exit(exit_code)
    login_dm()