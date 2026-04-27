import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import time
import os
from link import course_link_provider
from selenium.webdriver.chrome.options import Options
from driver_factory import create_driver


COURSE_URLS = []

PDF_PATH = os.path.join(PROJECT_ROOT, "Data", "Course_data.pdf")

from selenium.common.exceptions import WebDriverException
import time

import time

def safe_get(driver, url, retries=3):
    for i in range(retries):
        try:
            driver.get(url)
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Retry {i+1} failed for {url}: {e}")
            time.sleep(5)
    return False


def dict_to_paragraph_text(data: dict) -> str:
    text = ""
    for key, value in data.items():
        if isinstance(value, dict):
            text += f"<b>{key}</b><br/>"
            for k, v in value.items():
                text += f"- {k}: {v}<br/>"
        elif isinstance(value, list):
            text += f"<b>{key}</b><br/>"
            for item in value:
                text += f"- {item}<br/>"
        else:
            text += f"<b>{key}</b>: {value}<br/>"
        text += "<br/>"
    return text


def generate_pdf(course_data, pdf_path):
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    elements = []

    for course in course_data:
        elements.append(
            Paragraph(
                f"<b>{course.get('Course Title', 'Unnamed Course')}</b>",
                styles["Heading2"]
            )
        )
        elements.append(Spacer(1, 12))

        course_text = dict_to_paragraph_text(course)
        elements.append(Paragraph(course_text, styles["Normal"]))
        elements.append(Spacer(1, 20))

    doc.build(elements)


def scrape_course_data(driver, url):
    wait = WebDriverWait(driver, 20)
    if not safe_get(driver, url):
        print(f" Skipping URL after retries: {url}")
        return None


    data = {
        "Course Title": "",
        "Course Info": [],
        "Target Audience": [],
        "Syllabus": [],
        "Prerequisites": [],
        "Batch Schedule": {
            "Table": [],
            "Schedule Note": ""
        }
    }

    main_section = wait.until(
        EC.presence_of_element_located((By.ID, "course_cat"))
    )

    left_col = main_section.find_element(
        By.XPATH, ".//div[contains(@class,'col-sm-7') or contains(@class,'col-md-8')]"
    )

    data["Course Title"] = left_col.find_element(By.TAG_NAME, "h3").text.strip()

    course_info_div = left_col.find_element(
        By.CLASS_NAME, "course_info"
    )

    info_elements = course_info_div.find_elements(
        By.XPATH, ".//h3 | .//p"
    )

    for el in info_elements:
        text = el.text.strip()
        if text:
            data["Course Info"].append(text)

    accordion = left_col.find_element(By.ID, "accordion")
    panels = accordion.find_elements(By.CLASS_NAME, "panel")

    for panel in panels:
        heading = panel.find_element(By.CLASS_NAME, "panel-heading").text.strip()
        collapse = panel.find_element(By.CLASS_NAME, "panel-collapse")

        driver.execute_script(
            "arguments[0].classList.add('in'); arguments[0].style.height='auto';",
            collapse
        )

        time.sleep(0.3)

        items = collapse.find_elements(By.XPATH, ".//li | .//p")
        text_items = [i.text.strip() for i in items if i.text.strip()]

        if "Target" in heading:
            data["Target Audience"].extend(text_items)

        elif "Syllabus" in heading:
            data["Syllabus"].extend(text_items)

        elif "Pre" in heading:
            data["Prerequisites"].extend(text_items)

        elif "Batch" in heading:
            rows = collapse.find_elements(By.XPATH, ".//table//tr")
            for row in rows[1:]:
                cols = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
                if len(cols) >= 5:
                    data["Batch Schedule"]["Table"].append({
                        "Sr.No": cols[0],
                        "Batch Code": cols[1],
                        "Start Date": cols[2],
                        "End Date": cols[3],
                        "Time": cols[4]
                    })

            for text in text_items:
                if "Weekdays" in text or "Schedule" in text:
                    data["Batch Schedule"]["Schedule Note"] = text


    return data

def scrape_all_courses():
    """Scrape all courses and generate PDF"""
    all_courses = []
    
    # Move link provider call here
    COURSE_URLS = course_link_provider()
    
    driver = create_driver()

    try:
        for url in COURSE_URLS:
            print(f"Scraping: {url}")
            course = scrape_course_data(driver, url)
            if course:
                all_courses.append(course)
            time.sleep(2)

    finally:
        driver.quit()   # ✅ quit once

    generate_pdf(all_courses, PDF_PATH)
    print("✅ PDF created with multiple courses")
    return PDF_PATH


def main():
    scrape_all_courses()


if __name__ == "__main__":
    main()
