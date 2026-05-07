import time
import sys
import os
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Data_Scraping.driver_factory import create_driver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def course_link_provider():
    """Scrapes course links with retry logic and enhanced waiting."""
    URL = "https://sunbeaminfo.in/modular-courses-home"
    logger.info(f"Starting course link scraping from {URL}")

    driver = create_driver()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 45)

        # Wait for the body tag to exist
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Give JS extra time to render the dynamic content
        logger.info("Waiting for dynamic content to render...")
        time.sleep(8)
        
        # Scroll to bottom to trigger any lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Wait for the specific course links
        logger.info("Waiting for course link elements...")
        try:
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a.c_cat_more_btn")
                )
            )
        except TimeoutException:
            logger.warning("Initial wait for links timed out, attempting one more scroll...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        course_links = set()
        elements = driver.find_elements(By.CSS_SELECTOR, "a.c_cat_more_btn")
        
        for el in elements:
            href = el.get_attribute("href")
            if href:
                course_links.add(href)

        logger.info(f"Successfully found {len(course_links)} course links.")
        return list(course_links)

    except Exception as e:
        logger.error(f"Error during course link scraping: {str(e)}")
        # Log snippet of page source for debugging in CI
        logger.debug(f"Page source snippet: {driver.page_source[:2000]}")
        raise
    finally:
        driver.quit()
        logger.info("Driver closed.")

if __name__ == "__main__":
    links = course_link_provider()
    for link in links:
        print(link)
