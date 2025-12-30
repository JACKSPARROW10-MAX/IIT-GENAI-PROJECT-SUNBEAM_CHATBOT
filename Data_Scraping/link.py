from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
def course_link_provider():
    URL = "https://sunbeaminfo.in/modular-courses-home"

    # Chrome setup
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(URL)

    wait = WebDriverWait(driver, 15)

    # Wait until all "View More" links load
    wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a.c_cat_more_btn")
        )
    )

    # Extract only links
    course_links = set()

    elements = driver.find_elements(By.CSS_SELECTOR, "a.c_cat_more_btn")
    for el in elements:
        href = el.get_attribute("href")
        if href:
            course_links.add(href)

    driver.quit()

    # Print links
    for link in course_links:
        print(link)
    
    return course_links

