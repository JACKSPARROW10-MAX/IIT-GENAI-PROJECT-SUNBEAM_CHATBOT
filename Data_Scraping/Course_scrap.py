import sys
import os
import time
import logging
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Data_Scraping.link import course_link_provider
from Data_Scraping.driver_factory import create_driver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PDF_PATH = os.path.join(PROJECT_ROOT, "Data", "Course_data.pdf")

def safe_get(driver, url, retries=3):
    """Safely attempts to load a URL with retries."""
    for i in range(retries):
        try:
            logger.info(f"Loading URL (Attempt {i+1}): {url}")
            driver.get(url)
            time.sleep(4) # Allow content to settle
            return True
        except Exception as e:
            logger.warning(f"Attempt {i+1} failed for {url}: {str(e)}")
            time.sleep(5)
    return False

def dict_to_paragraph_text(data: dict) -> str:
    """Converts a data dictionary to HTML-like text for ReportLab paragraphs."""
    text = ""
    for key, value in data.items():
        if not value: continue
        if isinstance(value, dict):
            text += f"<b>{key}</b><br/>"
            for k, v in value.items():
                if v: text += f"- {k}: {v}<br/>"
        elif isinstance(value, list):
            if not value: continue
            text += f"<b>{key}</b><br/>"
            for item in value:
                if item: text += f"- {item}<br/>"
        else:
            text += f"<b>{key}</b>: {value}<br/>"
        text += "<br/>"
    return text

def generate_pdf(course_data, pdf_path):
    """Generates a structured PDF for all courses."""
    logger.info(f"Generating PDF for {len(course_data)} courses at {pdf_path}")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    elements = []

    for course in course_data:
        title = course.get('Course Title', 'Unnamed Course')
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 12))

        course_text = dict_to_paragraph_text(course)
        if course_text:
            elements.append(Paragraph(course_text, styles["Normal"]))
            elements.append(Spacer(1, 20))

    try:
        doc.build(elements)
        logger.info("PDF generation successful.")
    except Exception as e:
        logger.error(f"Error building PDF: {str(e)}")

def scrape_course_data(driver, url):
    """Scrapes detailed information for a single course."""
    wait = WebDriverWait(driver, 20)
    if not safe_get(driver, url):
        return None

    data = {
        "Course Title": "Unknown",
        "Course Info": [],
        "Target Audience": [],
        "Syllabus": [],
        "Prerequisites": [],
        "Batch Schedule": {
            "Table": [],
            "Schedule Note": ""
        }
    }

    try:
        main_section = wait.until(EC.presence_of_element_located((By.ID, "course_cat")))
        left_col = main_section.find_element(By.XPATH, ".//div[contains(@class,'col-sm-7') or contains(@class,'col-md-8')]")
        
        data["Course Title"] = left_col.find_element(By.TAG_NAME, "h3").text.strip()
        logger.info(f"Scraping Course: {data['Course Title']}")

        try:
            course_info_div = left_col.find_element(By.CLASS_NAME, "course_info")
            info_elements = course_info_div.find_elements(By.XPATH, ".//h3 | .//p")
            data["Course Info"] = [el.text.strip() for el in info_elements if el.text.strip()]
        except:
            logger.warning(f"Could not find course info for {data['Course Title']}")

        try:
            accordion = left_col.find_element(By.ID, "accordion")
            panels = accordion.find_elements(By.CLASS_NAME, "panel")

            for panel in panels:
                heading = panel.find_element(By.CLASS_NAME, "panel-heading").text.strip()
                collapse = panel.find_element(By.CLASS_NAME, "panel-collapse")

                # Force visibility for scraping
                driver.execute_script("arguments[0].classList.add('in'); arguments[0].style.height='auto';", collapse)
                time.sleep(0.5)

                items = collapse.find_elements(By.XPATH, ".//li | .//p")
                text_items = [i.text.strip() for i in items if i.text.strip()]

                if "Target" in heading:
                    data["Target Audience"].extend(text_items)
                elif "Syllabus" in heading:
                    data["Syllabus"].extend(text_items)
                elif "Pre" in heading:
                    data["Prerequisites"].extend(text_items)
                elif "Batch" in heading:
                    try:
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
                    except:
                        pass
                    for text in text_items:
                        if any(k in text for k in ["Weekdays", "Schedule", "Timing"]):
                            data["Batch Schedule"]["Schedule Note"] = text
        except Exception as e:
            logger.warning(f"Error scraping accordion for {data['Course Title']}: {str(e)}")

        return data
    except Exception as e:
        logger.error(f"Failed to scrape course data from {url}: {str(e)}")
        return None

def scrape_all_courses():
    """Coordinates the scraping of all discovered courses."""
    logger.info("Starting batch course scraping process...")
    
    course_urls = course_link_provider()
    if not course_urls:
        logger.error("No course URLs found to scrape.")
        return None
    
    logger.info(f"Found {len(course_urls)} courses to scrape.")
    all_courses = []
    driver = create_driver()

    try:
        for idx, url in enumerate(course_urls, start=1):
            logger.info(f"Processing course {idx}/{len(course_urls)}")
            course = scrape_course_data(driver, url)
            if course:
                all_courses.append(course)
            time.sleep(2)

        if all_courses:
            generate_pdf(all_courses, PDF_PATH)
            logger.info(f"Successfully scraped {len(all_courses)} courses.")
        else:
            logger.error("No course data was successfully scraped.")

    except Exception as e:
        logger.error(f"Fatal error in scrape_all_courses: {str(e)}")
    finally:
        driver.quit()
        logger.info("Driver closed.")

    return PDF_PATH

if __name__ == "__main__":
    scrape_all_courses()
