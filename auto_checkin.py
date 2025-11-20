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

# ==================== 配置区 ====================
USERNAME = os.getenv('ZENIX_USERNAME')
PASSWORD = os.getenv('ZENIX_PASSWORD')
TG_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

if not all([USERNAME, PASSWORD, TG_TOKEN, TG_CHAT_ID]):
    raise ValueError("请检查 GitHub Secrets 是否全部配置！")

# Telegram 发送消息函数
def send_tg(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass  # 失败也不影响主任务

# ==================== 随机延迟（实现每天真正随机时间） ====================
# 每小时第17分触发后，再随机睡 0~59 分钟 → 全天真正随机
random_minutes = random.randint(0, 59)
print(f"随机等待 {random_minutes} 分钟后开始执行...")
time.sleep(random_minutes * 60)

send_tg("🚀 Zenix 续期任务开始执行...")

# ==================== Selenium 配置 ====================
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

try:
    driver.get("https://dash.zenix.sg/login")
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)

    wait.until(EC.url_contains("/dashboard"))
    driver.get("https://dash.zenix.sg/dashboard/renew")
    time.sleep(3)

    # 超级稳的按钮定位
    renew_btn = wait.until(EC.element_to_be_clickable((By.XPATH,
        "//button[contains(translate(text(),'RENEW','renew'),'renew')]")))
    
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", renew_btn)
    time.sleep(1)
    renew_btn.click()

    send_tg("✅ <b>Zenix 续期成功！</b>\n流量已刷新～")
    print("续期成功！")

except Exception as e:
    error_msg = f"❌ <b>Zenix 续期失败！</b>\n错误：{str(e)[:200]}"
    send_tg(error_msg)
    driver.save_screenshot("error.png")
    print("续期失败：", e)
    raise e

finally:
    driver.quit()
