import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 从 GitHub Secrets 获取用户名和密码
username = os.getenv('ZENIX_USERNAME')  # 从 GitHub Secrets 获取用户名
password = os.getenv('ZENIX_PASSWORD')  # 从 GitHub Secrets 获取密码

if not username or not password:
    raise ValueError("请确保在 GitHub Secrets 中设置了 'ZENIX_USERNAME' 和 'ZENIX_PASSWORD'。")

# 设置 ChromeOptions，启用无头模式
chrome_options = Options()
chrome_options.add_argument('--headless')  # 无头模式
chrome_options.add_argument('--no-sandbox')  # 避免沙盒问题
chrome_options.add_argument('--disable-dev-shm-usage')  # 解决共享内存问题

# 设置 WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 打开登录页面
driver.get("https://dash.zenix.sg/login")

# 显式等待用户名输入框出现，确保页面加载完毕
wait = WebDriverWait(driver, 10)
username_field = wait.until(EC.presence_of_element_located((By.ID, "email")))  # 通过id定位用户名输入框

# 填写用户名和密码并提交
username_field.send_keys(username)
password_field = driver.find_element(By.ID, "password")  # 通过id定位密码输入框
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)  # 提交表单

# 等待登录完成，确保页面完全加载
time.sleep(5)

# 登录后进入到 renew 页面
driver.get("https://dash.zenix.sg/dashboard/renew")

# 每 5 分钟点击一次 "Renew All Servers"
try:
    while True:
        # 查找并点击 "Renew All Servers" 按钮
        renew_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Renew All Servers')]")
        renew_button.click()
        print("点击了 Renew All Servers 按钮！")

        # 等待 5 分钟（300秒）
        time.sleep(300)

except KeyboardInterrupt:
    print("脚本已停止。")
    driver.quit()
