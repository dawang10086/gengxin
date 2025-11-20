import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==================== 配置 ====================
USERNAME = os.getenv('ZENIX_USERNAME')
PASSWORD = os.getenv('ZENIX_PASSWORD')
TG_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

if not all([USERNAME, PASSWORD, TG_TOKEN, TG_CHAT_ID]):
    raise ValueError("Secrets 配置不完整，请检查 ZENIX_USERNAME / PASSWORD / TG_BOT_TOKEN / TG_CHAT_ID")

def send_tg(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
    except:
        pass  # 网络波动也不影响主任务

# ==================== 随机延迟：最多只等 3 分钟 ====================
delay = random.randint(0, 3)   # 0~3 分钟随机
print(f"随机等待 {delay} 分钟后开始执行...")
time.sleep(delay * 60)

send_tg("🚀 Zenix 续期任务启动中...（随机延迟 {delay} 分钟）".format(delay=delay))

# ==================== Selenium 无头浏览器 ====================
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

try:
    # 登录
    driver.get("https://dash.zenix.sg/login")
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)
    wait.until(EC.url_contains("/dashboard"))
    print("登录成功")

    # 进入续期页面并点击按钮
    driver.get("https://dash.zenix.sg/dashboard/renew")
    time.sleep(3)

    renew_btn = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//button[contains(translate(text(),'RENEW','renew'),'renew')]")))
    
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", renew_btn)
    time.sleep(1)
    renew_btn.click()

    send_tg("✅ <b>Zenix 续期成功！</b>\n流量已刷新～")
    print("续期成功，已发 TG 通知")

except Exception as e:
    error_msg = f"❌ <b>Zenix 续期失败</b>\n错误：{str(e)[:200]}"
    send_tg(error_msg)
    driver.save_screenshot("error.png")
    print("续期失败：", e)
    raise e

finally:
    driver.quit()
