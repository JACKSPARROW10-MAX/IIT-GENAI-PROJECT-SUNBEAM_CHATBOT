import sys
import os
import json
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Data_Scraping.driver_factory import create_driver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_precat_course(driver):
    """Scrapes the Pre-CAT course details."""
    URL = "https://sunbeaminfo.in/pre-cat"
    PDF_NAME = os.path.join(PROJECT_ROOT, "Data", "PreCAT_Course_Data.pdf")
    os.makedirs(os.path.dirname(PDF_NAME), exist_ok=True)

    logger.info(f"Navigating to Pre-CAT page: {URL}")
    driver.get(URL)
    wait = WebDriverWait(driver, 35)

    styles = getSampleStyleSheet()
    story = []

    try:
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3.inner_page_head")))
        title = title_el.text.strip()
        logger.info(f"Page Title: {title}")
        story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
        story.append(Spacer(1, 12))

        # Course Contents
        story.append(Paragraph("<b>Course Contents</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))

        try:
            toggle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#headingOne a")))
            driver.execute_script("arguments[0].click();", toggle)
            time.sleep(1)
        except:
            logger.warning("Could not click Course Contents toggle.")

        course_items = driver.find_elements(By.CSS_SELECTOR, "#collapse1 ul li")
        logger.info(f"Found {len(course_items)} course content items.")
        for i, item in enumerate(course_items, start=1):
            txt = item.text.strip()
            if txt:
                story.append(Paragraph(f"{i}. {txt}", styles["Normal"]))

        # Batch Schedule
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Batch Schedule</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))

        batch_schedule = []
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 4:
                    batch_schedule.append({
                        "Sr No": cols[0].text.strip(),
                        "Batch Code": cols[1].text.strip(),
                        "Duration": cols[2].text.strip(),
                        "Start Date": cols[3].text.strip()
                    })
            
            if batch_schedule:
                logger.info(f"Found {len(batch_schedule)} batches.")
                # Simple text representation of batch info
                for b in batch_schedule:
                    story.append(Paragraph(f"Batch {b['Batch Code']}: Starts {b['Start Date']}, Duration {b['Duration']}", styles["Normal"]))
            else:
                story.append(Paragraph("No batch schedule available", styles["Normal"]))
        except Exception as e:
            logger.warning(f"Error scraping batch table: {str(e)}")

        # Eligibility
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Eligibility Criteria</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))

        try:
            panels = driver.find_elements(By.CSS_SELECTOR, ".panel-body")
            # Usually the second panel-body is eligibility
            eligibility_text = ""
            for p in panels:
                if "graduation" in p.text.lower() or "eligibility" in p.text.lower():
                    eligibility_text = p.text.strip()
                    break
            
            if not eligibility_text and len(panels) > 1:
                eligibility_text = panels[1].text.strip()
            
            if eligibility_text:
                story.append(Paragraph(eligibility_text.replace("\n", "<br/>"), styles["Normal"]))
            else:
                story.append(Paragraph("Eligibility info not available", styles["Normal"]))
        except Exception as e:
            logger.warning(f"Error scraping eligibility: {str(e)}")

        # Build PDF
        logger.info(f"Building PDF: {PDF_NAME}")
        pdf = SimpleDocTemplate(PDF_NAME, pagesize=A4)
        pdf.build(story)
        logger.info("Pre-CAT PDF generation successful.")
        return PDF_NAME

    except Exception as e:
        logger.error(f"Fatal error scraping Pre-CAT: {str(e)}")
        raise

def scrape_precat_courses(driver):
    """Wrapper function for Pre-CAT scraping."""
    return scrape_precat_course(driver)

if __name__ == "__main__":
    driver = create_driver()
    try:
        scrape_precat_course(driver)
    finally:
        driver.quit()
