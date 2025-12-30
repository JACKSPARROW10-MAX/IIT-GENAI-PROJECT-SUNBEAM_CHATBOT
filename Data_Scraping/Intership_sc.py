from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
from Data.internship_pdf_gen import generate_internship_pdf

URL = "https://www.sunbeaminfo.in/internship"
OUTPUT_PDF = r"D:\Sunbeam\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\internship_data.pdf"


def scrape_internship_text():
    driver = webdriver.Chrome()
    driver.get(URL)
    time.sleep(3)

    all_text = []

    internship_section = driver.find_element(By.ID, "internship")

    outside_elements = internship_section.find_elements(
        By.XPATH,
        ".//*[self::p or self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6 "
        "or self::li or self::ul or self::ol or self::td or self::tr or self::span]"
    )

    for el in outside_elements:
        text = el.text.strip()
        if text and len(text) > 2:
            all_text.append(text)

    dropdown_ids = [
        "collapseOneA",
        "collapseTwo",
        "collapseThree",
        "collapseFour",
        "collapseFive",
        "collapseSix"
    ]

    for drop_id in dropdown_ids:
        try:
            dropdown = driver.find_element(By.ID, drop_id)

            driver.execute_script("""
                arguments[0].classList.add('in');
                arguments[0].style.height = 'auto';
                arguments[0].setAttribute('aria-expanded','true');
            """, dropdown)

            time.sleep(0.4)

            elements = dropdown.find_elements(
                By.XPATH,
                ".//*[self::p or self::li or self::h1 or self::h2 or self::h3 "
                "or self::h4 or self::h5 or self::h6 or self::span]"
            )

            for el in elements:
                text = el.text.strip()
                if text and len(text) > 2:
                    all_text.append(text)

        except Exception as e:
            print(f"Dropdown {drop_id} skipped: {e}")

    driver.quit()

    all_text = list(dict.fromkeys(all_text))

    return all_text


if __name__ == "__main__":
    internship_text = scrape_internship_text()
    generate_internship_pdf(internship_text, OUTPUT_PDF)
    print("✅ Internship PDF generated successfully")
