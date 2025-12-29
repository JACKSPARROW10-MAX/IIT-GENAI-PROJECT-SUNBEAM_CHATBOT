from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st

st.title("Course data Scrap")
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)
url = "https://sunbeaminfo.in/modular-courses/core-java-classes"

def scrape_course_basic_info(url):
    driver.get(url)

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    course_data = {}

    info_div = driver.find_element(By.CSS_SELECTOR, "div.course_info")

    lines = info_div.text.split("\n")

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            course_data[key.strip()] = value.strip()

    sections = {}

    accordion_headers = driver.find_elements(
    By.CSS_SELECTOR,
    "#accordion .panel-title a"
)

    for header in accordion_headers:
        title = header.text.strip()
        if not title:
            continue
        driver.execute_script("arguments[0].click();", header)
        collapse_id = header.get_attribute("href").split("#")[-1]

        content_div = wait.until(
            EC.presence_of_element_located((By.ID, collapse_id))
        )

        body = content_div.find_element(By.CLASS_NAME, "panel-body")

        sections[title] = body.text.strip()


    return course_data,sections


course_data,sections=scrape_course_basic_info(url)
st.write(course_data)
st.write(sections)