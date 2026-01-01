import os
import time
import textwrap

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Data_Scraping.driver_factory import create_driver


# --------------------------------------------------
# PDF GENERATION
# --------------------------------------------------
def generate_about_us_pdf(section_1, section_2):
    output_path = "../Data/about_us_data.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    x_margin = 1 * inch
    y_margin = 1 * inch
    text = pdf.beginText(x_margin, height - y_margin)

    text.setFont("Helvetica-Bold", 16)
    text.textLine("About Sunbeam")
    text.textLine("")

    sections = {
        "About Section": section_1,
        "Additional Information": section_2
    }

    for title, content in sections.items():
        if not content:
            continue

        text.setFont("Helvetica-Bold", 12)
        text.textLine(title)
        text.textLine("")

        text.setFont("Helvetica", 11)

        for paragraph in content:
            wrapped_lines = textwrap.wrap(paragraph, 90)
            for line in wrapped_lines:
                if text.getY() < y_margin:
                    pdf.drawText(text)
                    pdf.showPage()
                    text = pdf.beginText(x_margin, height - y_margin)
                    text.setFont("Helvetica", 11)
                text.textLine(line)
            text.textLine("")

    pdf.drawText(text)
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
    collected_data = []

    accordion_links = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.XPATH,
                "//div[@class='about_other_data accordion_outer_box']"
                "//h4[@class='panel-title']/a"
            )
        )
    )

    for link in accordion_links:
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", link
        )
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", link)

        collapse_id = link.get_attribute("href").split("#")[-1]

        panel_body = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//div[@id='{collapse_id}']//div[@class='panel-body']"
                )
            )
        )

        paragraphs = panel_body.find_elements(
            By.XPATH, ".//div[@class='list_style']//p"
        )

        for p in paragraphs:
            text = p.text.strip()
            if text:
                collected_data.append(text)

    return collected_data


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------
def main():
    driver = create_driver()

    try:
        driver.get("https://www.sunbeaminfo.com/about-us")

        section_1 = scrape_about_section_one(driver)
        section_2 = scrape_about_section_two(driver)

        pdf_path = generate_about_us_pdf(section_1, section_2)
        print(f"PDF generated at: {pdf_path}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
