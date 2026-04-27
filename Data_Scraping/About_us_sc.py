import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

import time
import textwrap

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from driver_factory import create_driver

# --------------------------------------------------
# PDF GENERATION
# --------------------------------------------------
def generate_about_us_pdf(section_1, section_2):
    output_path = os.path.join(PROJECT_ROOT, "Data", "about_us_data.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

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

    return output_path


# --------------------------------------------------
# SCRAPING FUNCTIONS
# --------------------------------------------------
def scrape_about_section_one(driver):
    wait = WebDriverWait(driver, 20)
    paragraphs = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "(//div[@class='main_info wow fadeInUp'])[1]//p")
        )
    )

    return [p.text.strip() for p in paragraphs if p.text.strip()]


def scrape_about_section_two(driver):
    wait = WebDriverWait(driver, 20)
    data = []

    accordion_links = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH,
             "//div[@class='about_other_data accordion_outer_box']"
             "//h4[@class='panel-title']/a")
        )
    )

    for link in accordion_links:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", link)

        collapse_id = link.get_attribute("href").split("#")[-1]

        panel_body = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//div[@id='{collapse_id}']//div[@class='panel-body']")
            )
        )

        paragraphs = panel_body.find_elements(By.XPATH, ".//div[@class='list_style']//p")
        for p in paragraphs:
            text = p.text.strip()
            if text and text != "\xa0":
                data.append(text)

    return data


# --------------------------------------------------
# MAIN
# --------------------------------------------------
def scrape_about():
    """Main function to scrape about us data"""
    driver = create_driver()

    try:
        driver.get("https://www.sunbeaminfo.com/about-us")

        section_1 = scrape_about_section_one(driver)
        section_2 = scrape_about_section_two(driver)

        pdf_path = generate_about_us_pdf(section_1, section_2)
        print("PDF generated at:", pdf_path)
        return pdf_path

    finally:
        driver.quit()


def main():
    scrape_about()


if __name__ == "__main__":
    main()
