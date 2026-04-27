import sys
import os
import json
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from .driver_factory import create_driver


def scrape_precat_course(driver):
    URL = "https://sunbeaminfo.in/pre-cat"
    PDF_NAME = os.path.join(PROJECT_ROOT, "Data", "PreCAT_Course_Data.pdf")

    os.makedirs(os.path.dirname(PDF_NAME), exist_ok=True)

    wait = WebDriverWait(driver, 40)
    driver.get(URL)

    styles = getSampleStyleSheet()
    story = []

    title = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h3.inner_page_head"))
    ).text.strip()

    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Course Contents</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    try:
        toggle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#headingOne a")))
        driver.execute_script("arguments[0].click();", toggle)
    except:
        pass

    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#collapse1 ul li")) > 0)

    course_items = driver.find_elements(By.CSS_SELECTOR, "#collapse1 ul li")
    course_list = []

    for i, item in enumerate(course_items, start=1):
        txt = item.text.strip()
        if txt:
            course_list.append(txt)
            story.append(Paragraph(f"{i}. {txt}", styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Batch Schedule (JSON)</b>", styles["Heading2"]))
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
    except:
        pass

    if batch_schedule:
        story.append(
            Paragraph(
                f"<pre>{json.dumps(batch_schedule, indent=2, ensure_ascii=False)}</pre>",
                styles["Normal"]
            )
        )
    else:
        story.append(Paragraph("No batch schedule available", styles["Normal"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Eligibility Criteria</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    panels = driver.find_elements(By.CSS_SELECTOR, ".panel-body")
    eligibility = panels[1].text.strip() if len(panels) > 1 else "Eligibility info not available"
    story.append(Paragraph(eligibility.replace("\n", "<br/>"), styles["Normal"]))

    pdf = SimpleDocTemplate(PDF_NAME, pagesize=A4)
    pdf.build(story)

    return {
        "title": title,
        "course_contents_count": len(course_list),
        "batch_count": len(batch_schedule),
        "pdf_path": PDF_NAME
    }


if __name__ == "__main__":
    driver = create_driver()
    try:
        result = scrape_precat_course(driver)
        print("✅ Pre-CAT scraping completed")
        print(result)
    finally:
        driver.quit()
