import sys
import os
import time
import logging
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from driver_factory import create_driver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_internships(driver):
    """Scrapes internship details from the Sunbeam website."""
    URL = "https://www.sunbeaminfo.in/internship"
    OUTPUT_PDF_PATH = os.path.join(PROJECT_ROOT, "Data", "internship_final.pdf")
    os.makedirs(os.path.dirname(OUTPUT_PDF_PATH), exist_ok=True)

    logger.info(f"Navigating to Internship page: {URL}")
    driver.get(URL)
    time.sleep(6) # Extended wait for dynamic content

    try:
        internship = driver.find_element(By.ID, "internship")
    except Exception as e:
        logger.error(f"Could not find main internship container: {str(e)}")
        return None

    static_before = []
    logger.info("Scraping static content before accordions...")
    try:
        for el in internship.find_elements(By.XPATH, ".//*[self::h2 or self::h3 or self::p or self::ul or self::table]"):
            # Ensure element is not inside an accordion panel
            parents = driver.execute_script("""
                let el = arguments[0];
                let parents = [];
                while (el.parentElement && el.parentElement.id !== 'internship') {
                    el = el.parentElement;
                    parents.push(el.className);
                }
                return parents;
            """, el)

            if not any("panel-collapse" in p for p in parents):
                tag = el.tag_name.lower()
                text = el.text.strip()
                if not text and tag != 'table': continue

                if tag in ("h2", "h3"):
                    static_before.append({"type": "title", "text": text})
                elif tag == "p":
                    static_before.append({"type": "text", "text": text})
                elif tag == "ul":
                    for li in el.find_elements(By.TAG_NAME, "li"):
                        if li.text.strip(): static_before.append({"type": "list_item", "text": li.text.strip()})
                elif tag == "table":
                    rows = []
                    for tr in el.find_elements(By.TAG_NAME, "tr"):
                        row = [c.text.strip() for c in tr.find_elements(By.XPATH, "./th|./td") if c.text.strip()]
                        if row: rows.append(row)
                    if rows: static_before.append({"type": "table", "data": rows})
    except Exception as e:
        logger.warning(f"Error during static content scraping: {str(e)}")

    dropdowns = []
    logger.info("Scraping internship accordions...")
    panel_groups = internship.find_elements(By.CLASS_NAME, "panel")

    for idx, panel in enumerate(panel_groups, start=1):
        try:
            heading = panel.find_element(By.CLASS_NAME, "panel-heading")
            title = heading.text.strip()
            logger.info(f"Processing panel {idx}/{len(panel_groups)}: {title}")

            link_el = heading.find_element(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link_el)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", link_el)

            collapse = panel.find_element(By.CLASS_NAME, "panel-collapse")
            driver.execute_script("arguments[0].classList.add('in'); arguments[0].style.height='auto';", collapse)
            time.sleep(0.8)

            dropdown_content = []
            for el in collapse.find_elements(By.XPATH, ".//*[self::h2 or self::h3 or self::p or self::ul or self::table]"):
                tag = el.tag_name.lower()
                text = el.text.strip()
                if not text and tag != 'table': continue

                if tag in ("h2", "h3"):
                    dropdown_content.append({"type": "subtitle", "text": text})
                elif tag == "p":
                    dropdown_content.append({"type": "text", "text": text})
                elif tag == "ul":
                    for li in el.find_elements(By.TAG_NAME, "li"):
                        if li.text.strip(): dropdown_content.append({"type": "list_item", "text": li.text.strip()})
                elif tag == "table":
                    rows = []
                    for tr in el.find_elements(By.TAG_NAME, "tr"):
                        row = [c.text.strip() for c in tr.find_elements(By.XPATH, "./th|./td") if c.text.strip()]
                        if row: rows.append(row)
                    if rows: dropdown_content.append({"type": "table", "data": rows})

            dropdowns.append({"title": title, "content": dropdown_content})
        except Exception as e:
            logger.warning(f"Error processing panel {idx}: {str(e)}")
            continue

    # Generate PDF
    logger.info(f"Generating PDF report: {OUTPUT_PDF_PATH}")
    doc = SimpleDocTemplate(OUTPUT_PDF_PATH, pagesize=A4, margin=0.75*inch)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1a237e'), spaceAfter=12)
    section_title_style = ParagraphStyle('SectionTitle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#283593'), spaceAfter=10, spaceBefore=16)
    text_style = ParagraphStyle('CustomBody', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=6)

    story = [Paragraph("Sunbeam Internship Information", title_style), Spacer(1, 20)]

    def add_to_story(items):
        for item in items:
            if item["type"] == "title": story.append(Paragraph(item["text"], section_title_style))
            elif item["type"] == "subtitle" or item["type"] == "text": story.append(Paragraph(item["text"], text_style))
            elif item["type"] == "list_item": story.append(Paragraph(f"• {item['text']}", text_style))
            elif item["type"] == "table" and item["data"]:
                t = Table(item["data"], repeatRows=1)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(t)
                story.append(Spacer(1, 10))

    add_to_story(static_before)
    for dd in dropdowns:
        story.append(Paragraph(dd["title"], section_title_style))
        add_to_story(dd["content"])

    try:
        doc.build(story)
        logger.info("Internship PDF generation successful.")
    except Exception as e:
        logger.error(f"Error building Internship PDF: {str(e)}")

    return OUTPUT_PDF_PATH

def scrape_all_internships(driver):
    """Wrapper function for scraping internships."""
    return scrape_internships(driver)

if __name__ == "__main__":
    driver = create_driver()
    try:
        scrape_internships(driver)
    finally:
        driver.quit()
