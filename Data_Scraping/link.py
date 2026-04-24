import time
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from driver_factory import create_driver



def get_driver():
    return create_driver()


def course_link_provider():
    URL = "https://sunbeaminfo.in/modular-courses-home"

    driver = get_driver()
    driver.get(URL)

    wait = WebDriverWait(driver, 60)

    try:
        # Wait for the body tag to exist
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Give JS extra time to render the dynamic content
        time.sleep(10)
        
        # Scroll to bottom to trigger any lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Wait for the specific course links
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a.c_cat_more_btn")
            )
        )
    except TimeoutException:
        print("TimeoutException occurred.")
        print("Current URL:", driver.current_url)
        print("Page Title:", driver.title)
        print("Page source snippet (first 5000 chars):")
        print(driver.page_source[:5000])
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
