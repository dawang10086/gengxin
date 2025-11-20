import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

username = os.getenv('ZENIX_USERNAME')
password = os.getenv('ZENIX_PASSWORD')

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
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
    wait.until(EC.url_contains("/dashboard"))

    driver.get("https://dash.zenix.sg/dashboard/renew")
    time.sleep(3)

    btn = wait.until(EC.element_to_be_clickable((By.XPATH, 
        "//button[contains(translate(text(),'RENEW','renew'),'renew')]")))
    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
    btn.click()

    print("Zenix 续期成功！")
finally:
    driver.quit()
