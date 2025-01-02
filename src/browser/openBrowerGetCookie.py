# 打开浏览器获取cookie

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.action_chains import ActionChains

def format_cookie(cookie_list: list):
    cookie_dict = {}
    for cookie in cookie_list:
        cookie_dict[cookie.get('name')] = {
            'value': cookie.get('value'),
            'domain': cookie.get('domain'),
            'path': cookie.get('path'),
            'expires': cookie.get('expires'),
            'size': cookie.get('size'),
            'httpOnly': cookie.get('httpOnly'),
            'secure': cookie.get('secure'),
            'sameSite': cookie.get('sameSite'),
        }
    return cookie_dict

def open_browser_get_cookie():
    try:
        # 设置 Chrome 选项
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 无头模式，如果需要的话

        # 初始化浏览器
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
        # 访问大麦网
        # driver.get("https://passport.damai.cn/login")
        # user_input = driver.find_element(By.XPATH, '//*[@id="fm-login-id"]')
        # user_input.send_keys('18616888888')
        
        # 访问大麦网登录页面
        driver.get("https://passport.damai.cn/login")
        # 等待页面加载
        time.sleep(3)  # 先等待页面基本加载
        
        # 切换到框架（如果登录框在iframe中）
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            driver.switch_to.frame(iframes[0])
        
        # 显式等待元素出现
        wait = WebDriverWait(driver, 2)  # 增加等待时间到10秒
        account_input = wait.until(
            EC.presence_of_element_located((By.ID, "fm-login-id"))
        )
        # 输入密码
        password_input = wait.until(
            EC.presence_of_element_located((By.ID, "fm-login-password"))
        )

        # 点击按钮
        login_button = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "button-low-light"))
        )
        # 输入账号
        account_input.send_keys('18838280615')
        # 延迟1秒
        time.sleep(1)
        # 输入密码
        password_input.send_keys('aa123456')
        # 延迟1秒
        time.sleep(1)
        # 输入完账号密码后 点击按钮
        login_button.click()

        # 获取cookie前切回主文档
        driver.switch_to.default_content()
        
        # 获取cookie
        cookies = driver.get_cookies()
        formatted_cookies = format_cookie(cookies)
        # 判断cookies 是否有_m_h5_tk 和 _m_h5_tk_enc
        if '_m_h5_tk' in formatted_cookies and '_m_h5_tk_enc' in formatted_cookies:
            print("获取cookie成功")
            return formatted_cookies
        else:
            print("获取cookie失败")
            # 这段代码延迟执行，为了等待滑块出现
            time.sleep(10)
            execute_slider(driver, wait, login_button)

        # 等待验证通过
        time.sleep(3)
        
        # 关闭浏览器
        # driver.quit()
        
        return formatted_cookies
        
    except Exception as e:
        print(f"获取Cookie时发生错误: {e}")
        return None

# 执行滑块逻辑
def execute_slider(driver, wait, login_button):
    # 确保有滑块在获取滑块
    # 获取滑块（滑块可能有、可能没有）
    try:
        # 隐式等待元素出现
        sloider_span = driver.find_element(By.ID, "nc_1_n1z")
        # sloider_span = wait.until(
        #     EC.presence_of_element_located((By.ID, "nc_1_n1z"))
        # )
        # 执行滑动操作
        action = ActionChains(driver)
        action.click_and_hold(sloider_span)
        action.move_by_offset(300, 0)  # 水平移动300像素
        action.release()
        action.perform()
        print("滑动成功")
        # 滑动成功后，等待3秒
        time.sleep(3)
        # 检测登录按钮是否可以点击
        login_button.click()
    except Exception as e:
        # 滑块不存在 就延迟3秒，在调用一次
        print("滑块不存在", e.msg)
        # time.sleep(3)
        # execute_slider(driver, wait, login_button)

# 如果直接运行此文件
if __name__ == "__main__":
    cookies = open_browser_get_cookie()
    if cookies:
        print("Cookie获取成功:", cookies)
    else:
        print("Cookie获取失败")

