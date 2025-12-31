from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, os, json

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT


URL = "https://www.sunbeaminfo.in/internship"
OUTPUT_PDF_PATH = r"D:\SUNBEAM PROJECT\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\internship_final.pdf"


# ---------------- MAIN ----------------
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get(URL)
time.sleep(5)

internship = driver.find_element(By.ID, "internship")

# Step 1: Collect STATIC content BEFORE dropdowns
static_before = []
for el in internship.find_elements(By.XPATH, ".//*[self::h2 or self::h3 or self::p or self::ul or self::table]"):
    # Check if element is inside a panel-collapse (dropdown content)
    parents = driver.execute_script("""
        let el = arguments[0];
        let parents = [];
        while (el.parentElement) {
            el = el.parentElement;
            parents.push(el.className);
        }
        return parents;
    """, el)
    
    # If not inside dropdown, it's static content before dropdowns
    if not any("panel-collapse" in p for p in parents):
        tag = el.tag_name.lower()
        
        if tag in ("h2", "h3"):
            static_before.append({"type": "title", "text": el.text.strip()})
        elif tag == "p":
            txt = el.text.strip()
            if txt:
                static_before.append({"type": "text", "text": txt})
        elif tag == "ul":
            for li in el.find_elements(By.TAG_NAME, "li"):
                txt = li.text.strip()
                if txt:
                    static_before.append({"type": "list_item", "text": txt})
        elif tag == "table":
            rows = []
            for tr in el.find_elements(By.TAG_NAME, "tr"):
                row = [c.text.strip() for c in tr.find_elements(By.XPATH, "./th|./td") if c.text.strip()]
                if row:
                    rows.append(row)
            if rows:
                static_before.append({"type": "table", "data": rows})

# Step 2: Expand all dropdowns and collect dropdown sections
dropdowns = []
panel_groups = internship.find_elements(By.CLASS_NAME, "panel")

for panel in panel_groups:
    try:
        # Get dropdown title
        heading = panel.find_element(By.CLASS_NAME, "panel-heading")
        title_el = heading.find_element(By.TAG_NAME, "a")
        title = title_el.text.strip()
        
        # Find and expand the collapse section
        collapse = panel.find_element(By.CLASS_NAME, "panel-collapse")
        driver.execute_script(
            "arguments[0].classList.add('in'); arguments[0].style.height='auto';", 
            collapse
        )
        time.sleep(0.5)
        
        # Scrape content inside this dropdown
        dropdown_content = []
        
        for el in collapse.find_elements(By.XPATH, ".//*[self::h2 or self::h3 or self::p or self::ul or self::table]"):
            tag = el.tag_name.lower()
            
            if tag in ("h2", "h3"):
                dropdown_content.append({"type": "subtitle", "text": el.text.strip()})
            elif tag == "p":
                txt = el.text.strip()
                if txt:
                    dropdown_content.append({"type": "text", "text": txt})
            elif tag == "ul":
                for li in el.find_elements(By.TAG_NAME, "li"):
                    txt = li.text.strip()
                    if txt:
                        dropdown_content.append({"type": "list_item", "text": txt})
            elif tag == "table":
                rows = []
                for tr in el.find_elements(By.TAG_NAME, "tr"):
                    row = [c.text.strip() for c in tr.find_elements(By.XPATH, "./th|./td") if c.text.strip()]
                    if row:
                        rows.append(row)
                if rows:
                    dropdown_content.append({"type": "table", "data": rows})
        
        dropdowns.append({
            "title": title,
            "content": dropdown_content
        })
        
    except Exception as e:
        print(f"Error processing panel: {e}")
        continue

# Step 3: Collect STATIC content AFTER dropdowns
static_after = []
all_panels = internship.find_elements(By.CLASS_NAME, "panel")
if all_panels:
    last_panel = all_panels[-1]
    # Get all siblings after the last panel
    following_elements = driver.execute_script("""
        let panel = arguments[0];
        let siblings = [];
        let next = panel.nextElementSibling;
        while (next) {
            siblings.push(next);
            next = next.nextElementSibling;
        }
        return siblings;
    """, last_panel)
    
    for el in following_elements:
        try:
            tag = el.tag_name.lower()
            
            if tag in ("h2", "h3"):
                static_after.append({"type": "title", "text": el.text.strip()})
            elif tag == "p":
                txt = el.text.strip()
                if txt:
                    static_after.append({"type": "text", "text": txt})
            elif tag == "ul":
                for li in el.find_elements(By.TAG_NAME, "li"):
                    txt = li.text.strip()
                    if txt:
                        static_after.append({"type": "list_item", "text": txt})
            elif tag == "table":
                rows = []
                for tr in el.find_elements(By.TAG_NAME, "tr"):
                    row = [c.text.strip() for c in tr.find_elements(By.XPATH, "./th|./td") if c.text.strip()]
                    if row:
                        rows.append(row)
                if rows:
                    static_after.append({"type": "table", "data": rows})
        except:
            continue

driver.quit()

# ---------------- CREATE JSON STRUCTURE ----------------
json_data = {
    "source_url": URL,
    "scraped_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "structure": {
        "static_before": static_before,
        "dropdowns": dropdowns,
        "static_after": static_after
    }
}

# ---------------- PDF WITH JSON CONTENT ----------------
os.makedirs(os.path.dirname(OUTPUT_PDF_PATH), exist_ok=True)

doc = SimpleDocTemplate(
    OUTPUT_PDF_PATH,
    pagesize=A4,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    topMargin=0.75 * inch,
    bottomMargin=0.75 * inch
)

styles = getSampleStyleSheet()

# Create a custom style for JSON code
code_style = ParagraphStyle(
    'Code',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=8,
    leading=10,
    leftIndent=0,
    rightIndent=0,
    alignment=TA_LEFT,
    spaceAfter=0,
    spaceBefore=0
)

story = []

# Title
story.append(Paragraph("Internship Information - JSON Format", styles["Title"]))
story.append(Spacer(1, 20))

# Convert JSON to formatted string
json_string = json.dumps(json_data, indent=2, ensure_ascii=False)

# Split JSON into lines and add to PDF
json_lines = json_string.split('\n')

for line in json_lines:
    # Use Preformatted to preserve spacing and indentation
    story.append(Preformatted(line, code_style))

doc.build(story)

print(f"✅ PDF with JSON data generated: {OUTPUT_PDF_PATH}")
print(f"\nData Structure:")
print(f"   - Static content before dropdowns: {len(json_data['structure']['static_before'])} items")
print(f"   - Dropdown sections: {len(json_data['structure']['dropdowns'])} sections")
print(f"   - Static content after dropdowns: {len(json_data['structure']['static_after'])} items")