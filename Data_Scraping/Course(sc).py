from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

def scrape_course_basic_info(url):
    driver.get(url)

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

    data = {}
    data["url"] = url

    # Course name
    data["course_name"] = driver.find_element(By.TAG_NAME, "h1").text.strip()

    # Course info box
    info_box = driver.find_element(By.CSS_SELECTOR, ".col-md-8")
    lines = info_box.text.split("\n")

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    return data
