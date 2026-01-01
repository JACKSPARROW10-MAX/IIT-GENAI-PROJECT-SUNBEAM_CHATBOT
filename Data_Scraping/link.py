from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=chrome_options)


def course_link_provider():
    URL = "https://sunbeaminfo.in/modular-courses-home"

    driver = get_driver()
    driver.get(URL)

    wait = WebDriverWait(driver, 15)

    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a.c_cat_more_btn")
        )
    )

    course_links = set()

    elements = driver.find_elements(By.CSS_SELECTOR, "a.c_cat_more_btn")
    for el in elements:
        href = el.get_attribute("href")
        if href:
            course_links.add(href)

    driver.quit()

    for link in course_links:
        print(link)

    return course_links
