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
from Data_Scraping.link import course_link_provider
from selenium.webdriver.chrome.options import Options



COURSE_URLS = []
COURSE_URLS = course_link_provider()

PDF_PATH = r"D:\SUNBEAM PROJECT\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\Course_data.pdf"


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


def scrape_course_data(URL):
        
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gcm")
    options.add_argument("--disable-sync")
    options.add_argument("--log-level=3")   # hides warnings/errors
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options)
    wait = WebDriverWait(driver, 20)
    driver.get(URL)

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

    driver.quit()
    return data


if __name__ == "__main__":

    all_courses = []

    for url in COURSE_URLS:
        print(f"Scraping: {url}")
        course = scrape_course_data(url)
        all_courses.append(course)

    generate_pdf(all_courses, PDF_PATH)

    print("✅ PDF created with multiple courses")
