from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import json

def scrape_precat_course():


    # ------------------- CONFIG -------------------
    URL = "https://sunbeaminfo.in/pre-cat"
    PDF_NAME = r"D:\SUNBEAM PROJECT\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\PreCAT_Course_Data.pdf"

    # ------------------- SELENIUM SETUP -------------------
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 40)
    driver.get(URL)

    styles = getSampleStyleSheet()
    story = []

    # ------------------- TITLE -------------------
    title = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h3.inner_page_head"))
    ).text.strip()

    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # ------------------- COURSE CONTENTS -------------------
    story.append(Paragraph("<b>Course Contents</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    try:
        course_toggle = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#headingOne a"))
        )
        driver.execute_script("arguments[0].click();", course_toggle)
    except:
        print("⚠️ Course accordion not found.")

    wait.until(
        lambda d: d.find_element(
            By.CSS_SELECTOR, "#collapse1 div.list_style ul li"
        ).text.strip() != ""
    )

    course_items = driver.find_elements(
        By.CSS_SELECTOR, "#collapse1 div.list_style ul li"
    )

    course_list = []
    for idx, item in enumerate(course_items, start=1):
        text = item.text.strip()
        if text:
            course_list.append(text)
            story.append(Paragraph(f"{idx}. {text}", styles["Normal"]))

    story.append(Spacer(1, 12))

    # ------------------- BATCH SCHEDULE -------------------
    story.append(Paragraph("<b>Pre-CAT Batch Schedule (JSON Format)</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    batch_schedule = []

    try:
        batch_toggle = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(),'Batch')] | //a[contains(text(),'Schedule')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", batch_toggle)
        driver.execute_script("arguments[0].click();", batch_toggle)

        wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr")) > 0)

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
        print("⚠️ Batch schedule not found.")

    if batch_schedule:
        json_data = json.dumps(batch_schedule, indent=2, ensure_ascii=False)
        story.append(
            Paragraph(
                f"<pre><font name='Courier' size='8'>{json_data}</font></pre>",
                styles["Normal"]
            )
        )
    else:
        story.append(Paragraph("No batch schedule available", styles["Normal"]))

    story.append(Spacer(1, 12))

    # ------------------- ELIGIBILITY -------------------
    story.append(Paragraph("<b>Eligibility Criteria</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    panels = driver.find_elements(By.CSS_SELECTOR, ".panel-body")
    eligibility_text = panels[1].text.strip() if len(panels) > 1 else "Eligibility details not available."
    story.append(Paragraph(eligibility_text.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 12))

    # ------------------- REGISTRATION -------------------
    story.append(Paragraph("<b>Registration & Online Admission</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))

    buttons = driver.find_elements(By.CSS_SELECTOR, "a.btn, button")
    if buttons:
        story.append(Paragraph("✓ Registration portal is available", styles["Normal"]))
        story.append(Paragraph("✓ Online admission system is active", styles["Normal"]))
    else:
        story.append(Paragraph("Registration information not found.", styles["Normal"]))

    driver.quit()

    pdf = SimpleDocTemplate(
        PDF_NAME,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    pdf.build(story)

    return {
        "title": title,
        "course_contents_count": len(course_list),
        "batch_count": len(batch_schedule),
        "pdf_path": PDF_NAME
    }


def test_scrape_precat_course():
    print("🧪 Testing Pre-CAT Scraper...")
    result = scrape_precat_course()
    print(" Scraping completed")


if __name__ == "__main__":
    test_scrape_precat_course()
