from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException



def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=chrome_options)


def course_link_provider():
    URL = "https://sunbeaminfo.in/modular-courses-home"

    driver = get_driver()
    driver.get(URL)

    wait = WebDriverWait(driver, 60)

    try:
        # First wait for the root element to ensure the SPA has started loading
        wait.until(EC.presence_of_element_located((By.ID, "root")))
        
        # Then wait for the specific course links
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "a.c_cat_more_btn")
            )
        )
    except TimeoutException:
        print("TimeoutException occurred. Current URL:", driver.current_url)
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
