import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==================== 1. 从 Secrets 读取账号密码 ====================
username = os.getenv('ZENIX_USERNAME')
password = os.getenv('ZENIX_PASSWORD')
if not username or not password:
    raise ValueError("请在 GitHub Secrets 中设置 ZENIX_USERNAME 和 ZENIX_PASSWORD！")

# ==================== 2. Chrome 无头配置（GitHub Actions 专用） ====================
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')  # 固定分辨率防布局错乱

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

wait = WebDriverWait(driver, 20)   # 全局等待，最多等 20 秒

try:
    print("正在打开登录页面...")
    driver.get("https://dash.zenix.sg/login")

    # ==================== 3. 登录 ====================
    print("填写用户名和密码...")
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

    # 等待登录成功（通过判断 URL 变化或页面元素）
    wait.until(EC.url_contains("/dashboard"))
    print("登录成功！")

    # ==================== 4. 直接进入 renew 页面 ====================
    print("跳转到续期页面...")
    driver.get("https://dash.zenix.sg/dashboard/renew")
    time.sleep(3)  # 给页面一点渲染时间

    # ==================== 5. 无限循环点击续期按钮 ====================
    loop_count = 0
    while True:
        loop_count += 1
        print(f"\n第 {loop_count} 次尝试点击续期按钮...")

        # 打印当前页面所有可见按钮文字（调试神器）
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print("当前页面可见按钮数量:", len(buttons))
        for i, btn in enumerate(buttons):
            text = btn.text.strip()
            if text:
                print(f"  按钮 {i}: [{text}]")

        # 超级宽松的定位策略（支持当前所有已知写法）
        renew_button = None
        try:
            renew_button = wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(translate(text(), 'RENEW', 'renew'), 'renew') "
                    "or contains(text(), 'All') "
                    "or contains(text(), '全部') "
                    "or contains(text(), '续期') "
                    "or .//i[contains(@class, 'arrow') or contains(@class, 'rotate')]]"))  # 匹配旋转箭头图标
            )
        except:
            pass

        if not renew_button:
            # 第二套备用方案：找包含 “renew” 的任意可点击元素（有些面板把按钮改成 div）
            try:
                renew_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//*[contains(translate(text(), 'RENEW', 'renew'), 'renew') and (self::button or self::div or self::span)]"))
                )
            except:
                pass

        if renew_button:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", renew_button)
            time.sleep(1)
            renew_button.click()
            print("成功点击续期按钮！")
        else:
            print("未找到续期按钮，保存截图以供排查...")
            driver.save_screenshot(f"error_no_button_{int(time.time())}.png")
            # 即使没点到也继续等下一次，防止脚本直接退出
            print("10 秒后重试...")

        # 每 5 分钟执行一次（300 秒）
        print("等待 5 分钟后进行下一次续期...")
        time.sleep(300)

except Exception as e:
    print("脚本发生异常:", str(e))
    driver.save_screenshot("final_error.png")  # 最后再留个现场
    raise e
finally:
    # GitHub Actions 里可以不 quit，反正容器会销毁
    driver.quit()
