from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException



def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    return webdriver.Chrome(options=chrome_options)


def course_link_provider():
    URL = "https://sunbeaminfo.in/modular-courses-home"

    driver = get_driver()
    driver.get(URL)

    wait = WebDriverWait(driver, 30)

    try:
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a.c_cat_more_btn")
            )
        )
    except TimeoutException:
        print("TimeoutException occurred. Page source snippet:")
        print(driver.page_source[:2000])
        raise

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
