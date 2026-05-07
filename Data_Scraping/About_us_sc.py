import sys
import os
import time
import textwrap
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_factory import create_driver

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_about_us_pdf(section_1, section_2):
    """Generates a PDF from the scraped About Us data."""
    output_path = os.path.join(PROJECT_ROOT, "Data", "about_us_data.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"Generating PDF at {output_path}")
    pdf = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    x_margin = 1 * inch
    y_margin = 1 * inch
    text_obj = pdf.beginText(x_margin, height - y_margin)

    text_obj.setFont("Helvetica-Bold", 16)
    text_obj.textLine("About Sunbeam")
    text_obj.textLine("")

    sections = {
        "About Section": section_1,
        "Additional Information": section_2
    }

    for title, content in sections.items():
        if not content:
            continue

        text_obj.setFont("Helvetica-Bold", 12)
        text_obj.textLine(title)
        text_obj.textLine("")

        text_obj.setFont("Helvetica", 11)

        for para in content:
            wrapped = textwrap.wrap(para, 90)
            for line in wrapped:
                if text_obj.getY() < y_margin:
                    pdf.drawText(text_obj)
                    pdf.showPage()
                    text_obj = pdf.beginText(x_margin, height - y_margin)
                    text_obj.setFont("Helvetica", 11)
                text_obj.textLine(line)
            text_obj.textLine("")

    pdf.drawText(text_obj)
    pdf.save()
    logger.info("PDF generation completed.")
    return output_path

def scrape_about_section_one(driver):
    """Scrapes the first section of the About Us page."""
    logger.info("Scraping About Us Section One...")
    wait = WebDriverWait(driver, 25)
    try:
        paragraphs = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//div[@class='main_info wow fadeInUp'])[1]//p")
            )
        )
        return [p.text.strip() for p in paragraphs if p.text.strip()]
    except Exception as e:
        logger.warning(f"Could not find section one paragraphs: {str(e)}")
        return []

def scrape_about_section_two(driver):
    """Scrapes the accordion sections of the About Us page."""
    logger.info("Scraping About Us Section Two (Accordions)...")
    wait = WebDriverWait(driver, 25)
    data = []

    try:
        accordion_links = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='about_other_data accordion_outer_box']//h4[@class='panel-title']/a")
            )
        )

        for link in accordion_links:
            title = link.text.strip()
            logger.info(f"Opening accordion: {title}")
            
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", link)

            collapse_id = link.get_attribute("href").split("#")[-1]
            try:
                panel_body = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//div[@id='{collapse_id}']//div[@class='panel-body']")
                    )
                )
                paragraphs = panel_body.find_elements(By.XPATH, ".//div[@class='list_style']//p | .//p")
                for p in paragraphs:
                    text = p.text.strip()
                    if text and text != "\xa0":
                        data.append(text)
            except Exception as e:
                logger.warning(f"Timeout or error opening accordion {title}: {str(e)}")
                continue

        return data
    except Exception as e:
        logger.error(f"Error scraping Section Two: {str(e)}")
        return []

def scrape_about():
    """Main function to scrape about us data."""
    URL = "https://www.sunbeaminfo.com/about-us"
    logger.info(f"Starting About Us scraping from {URL}")
    driver = create_driver()

    try:
        driver.get(URL)
        section_1 = scrape_about_section_one(driver)
        section_2 = scrape_about_section_two(driver)

        if not section_1 and not section_2:
            logger.error("No data scraped from About Us page.")
            return None

        pdf_path = generate_about_us_pdf(section_1, section_2)
        return pdf_path

    except Exception as e:
        logger.error(f"Fatal error in scrape_about: {str(e)}")
        raise
    finally:
        driver.quit()
        logger.info("Driver closed.")

if __name__ == "__main__":
    scrape_about()
