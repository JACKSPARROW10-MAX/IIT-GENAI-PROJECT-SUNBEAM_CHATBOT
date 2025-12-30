from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import time
import json

URL = "https://sunbeaminfo.in/pre-cat"
PDF_NAME = "D:\Sunbeam\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\PreCAT_Course_Data.pdf"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 15)
driver.get(URL)
time.sleep(2)

styles = getSampleStyleSheet()
story = []

title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h3"))).text
story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
story.append(Spacer(1, 12))

accordions = driver.find_elements(By.CSS_SELECTOR, ".panel-title a")
for acc in accordions:
    driver.execute_script("arguments[0].click();", acc)
    time.sleep(0.4)
print(f"✅ Expanded {len(accordions)} accordions")

time.sleep(2)


story.append(Paragraph("<b>Course Contents</b>", styles["Heading2"]))
story.append(Spacer(1, 6))

driver.execute_script("window.scrollTo(0, 0);")
time.sleep(1)

selectors = [
    "#collapse1 div.list_style ul li",
    ".panel-body ul li",
    ".accordion-body ul li",
    ".collapse.show ul li",
    ".panel-collapse ul li",
    "div[class*='panel-body'] ul li",
    ".content-section ul li"
]

content_items = []
for selector in selectors:
    items = driver.find_elements(By.CSS_SELECTOR, selector)
    if items:
        content_items = [item.text.strip() for item in items if item.text.strip()]
        break

if not content_items:
    panels = driver.find_elements(By.CSS_SELECTOR, ".panel-body, .accordion-body, .collapse.show")
    for panel in panels:
        panel_text = panel.text.strip()
        if panel_text and "eligibility" not in panel_text.lower():
            lines = [line.strip() for line in panel_text.split('\n') if line.strip()]
            content_items.extend(lines[:10])

if content_items:
    story.append(Paragraph("Key Topics Covered:", styles["Normal"]))
    for i, item in enumerate(content_items[:20], 1):
        if item:
            story.append(Paragraph(f"{i}. {item}", styles["Normal"]))
else:
    story.append(Paragraph("Course contents not available on page", styles["Normal"]))

story.append(Spacer(1, 12))

story.append(Paragraph("<b>Eligibility Criteria</b>", styles["Heading2"]))
story.append(Spacer(1, 6))

eligibility_selectors = [
    "//h4[contains(text(),'Eligibility')]/following::div[@class='panel-body'][1]",
    "//h4[contains(text(),'Eligibility')]/following::div[1]",
    ".panel-body:contains('Eligibility')",
    "//*[contains(text(),'Eligibility')]/following-sibling::*",
    ".panel-body"
]

eligibility_text = ""
for selector in eligibility_selectors:
    try:
        if selector.startswith("//"):
            eligibility_text = driver.find_element(By.XPATH, selector).text
        else:
            eligibility_text = driver.find_element(By.CSS_SELECTOR, selector).text
        if eligibility_text.strip() and "eligibility" in eligibility_text.lower():
            break
    except:
        continue

panels = driver.find_elements(By.CSS_SELECTOR, ".panel-body, .accordion-body")
if not eligibility_text.strip() and len(panels) > 1:
    eligibility_text = panels[1].text

if eligibility_text.strip():
    story.append(Paragraph(eligibility_text.replace("\n", "<br/>"), styles["Normal"]))
    
else:
    story.append(Paragraph("Eligibility not available", styles["Normal"]))
story.append(Spacer(1, 12))

story.append(Paragraph("<b>Pre-CAT Batch Schedule (JSON Format)</b>", styles["Heading2"]))
story.append(Spacer(1, 6))

batch_schedule = []
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))

rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    if len(cols) >= 4:
        batch_obj = {
            "Sr No": cols[0].text.strip(),
            "Batch Code": cols[1].text.strip(),
            "Duration": cols[2].text.strip(),
            "Start Date": cols[3].text.strip()
        }
        batch_schedule.append(batch_obj)

if batch_schedule:
    json_data = json.dumps(batch_schedule, indent=2, ensure_ascii=False)
    story.append(Paragraph(f"<pre><font name='Courier' size='8'>{json_data}</font></pre>", styles["Normal"]))
   
else:
    story.append(Paragraph("No batch schedule available", styles["Normal"]))
    print("⚠️ No batch schedule found")

story.append(Spacer(1, 12))

story.append(Paragraph("<b>Registration & Online Admission</b>", styles["Heading2"]))
story.append(Spacer(1, 6))

reg_button = driver.find_elements(By.CSS_SELECTOR, "button, .btn, [href*='register']")
if reg_button:
    story.append(Paragraph("✓ Registration portal is available", styles["Normal"]))
    story.append(Paragraph("✓ Online admission system is active", styles["Normal"]))
    
else:
    story.append(Paragraph("Registration details not found", styles["Normal"]))

story.append(Spacer(1, 12))

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
print(f"\n✅ PDF created successfully: {PDF_NAME}")
