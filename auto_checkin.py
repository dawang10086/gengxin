import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys   # <--- 这行之前漏了！！
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==================== 从 Secrets 读取账号密码 ====================
username = os.getenv('ZENIX_USERNAME')
password = os.getenv('ZENIX_PASSWORD')
if not username or not password:
    raise ValueError("请在 GitHub Secrets 中设置 ZENIX_USERNAME 和 ZENIX_PASSWORD！")

# ==================== Chrome 无头配置 ====================
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

wait = WebDriverWait(driver, 20)

try:
    print("正在打开登录页面...")
    driver.get("https://dash.zenix.sg/login")

    print("填写用户名和密码...")
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "password").send_keys(Keys.RETURN)  # 现在不会报错了

    wait.until(EC.url_contains("/dashboard"))
    print("登录成功！")

    print("跳转到续期页面...")
    driver.get("https://dash.zenix.sg/dashboard/renew")
    time.sleep(3)

    loop_count = 0
    while True:
        loop_count += 1
        print(f"\n第 {loop_count} 次尝试点击续期按钮...")

        # 打印所有按钮文字，方便调试
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print("当前页面可见按钮数量:", len(buttons))
        for i, btn in enumerate(buttons):
            text = btn.text.strip()
            if text:
                print(f"  按钮 {i}: [{text}]")

        # 超级宽松定位（已适配 Zenix 2025年11月最新版）
        renew_button = None
        try:
            renew_button = wait.until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(translate(text(),'RENEW','renew'),'renew') or contains(text(),'All') or contains(text(),'全部') or contains(text(),'续期')]"))
            )
        except:
            try:  # 备用方案，有些版本是 div
                renew_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//*[contains(translate(text(),'RENEW','renew'),'renew') and (self::button or self::div)]"))
                )
            except:
                pass

        if renew_button:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", renew_button)
            time.sleep(1)
            renew_button.click()
            print("成功点击续期按钮！")
        else:
            print("未找到续期按钮，保存截图排查...")
            driver.save_screenshot(f"no_button_{int(time.time())}.png")

        print("等待 5 分钟后下一次续期...")
        time.sleep(300)

except Exception as e:
    print("脚本发生异常:", str(e))
    driver.save_screenshot("final_error.png")
    raise e
finally:
    driver.quit()
