import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from driver_factory import create_driver

def scrape_internships(driver):
    URL = "https://www.sunbeaminfo.in/internship"
    OUTPUT_PDF_PATH = os.path.join(PROJECT_ROOT, "Data", "internship_final.pdf")
    driver.get(URL)
    time.sleep(5)

    internship = driver.find_element(By.ID, "internship")

    static_before = []
    for el in internship.find_elements(By.XPATH, ".//*[self::h2 or self::h3 or self::p or self::ul or self::table]"):
        parents = driver.execute_script("""
            let el = arguments[0];
            let parents = [];
            while (el.parentElement) {
                el = el.parentElement;
                parents.push(el.className);
            }
            return parents;
        """, el)

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

    dropdowns = []
    panel_groups = internship.find_elements(By.CLASS_NAME, "panel")

    for panel in panel_groups:
        try:
            heading = panel.find_element(By.CLASS_NAME, "panel-heading")
            title_el = heading.find_element(By.TAG_NAME, "a")
            title = title_el.text.strip()

            collapse = panel.find_element(By.CLASS_NAME, "panel-collapse")
            driver.execute_script(
                "arguments[0].classList.add('in'); arguments[0].style.height='auto';",
                collapse
            )
            time.sleep(0.5)

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

            dropdowns.append({"title": title, "content": dropdown_content})

        except Exception as e:
            print(f"Error processing panel: {e}")
            continue

    static_after = []
    all_panels = internship.find_elements(By.CLASS_NAME, "panel")
    if all_panels:
        last_panel = all_panels[-1]
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

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=12,
        spaceBefore=12,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#283593'),
        spaceAfter=10,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#3949ab'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    text_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )

    list_style = ParagraphStyle(
        'ListItem',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10,
        fontName='Helvetica'
    )

    story = []
    story.append(Paragraph("Sunbeam Internship Information", title_style))
    story.append(Spacer(1, 20))

    def add_content_items(items, story):
        for item in items:
            if item["type"] == "title":
                story.append(Paragraph(item["text"], section_title_style))
            elif item["type"] == "subtitle":
                story.append(Paragraph(item["text"], subtitle_style))
            elif item["type"] == "text":
                story.append(Paragraph(item["text"], text_style))
            elif item["type"] == "list_item":
                story.append(Paragraph(f"• {item['text']}", list_style))
            elif item["type"] == "table" and item["data"]:
                t = Table(item["data"], repeatRows=1)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(t)
                story.append(Spacer(1, 10))

    if static_before:
        add_content_items(static_before, story)
        story.append(Spacer(1, 20))

    for dropdown in dropdowns:
        story.append(Paragraph(dropdown["title"], section_title_style))
        add_content_items(dropdown["content"], story)
        story.append(Spacer(1, 16))

    if static_after:
        add_content_items(static_after, story)

    doc.build(story)

    print(f"✅ PDF generated: {OUTPUT_PDF_PATH}")

    return {
        "static_before": static_before,
        "dropdowns": dropdowns,
        "static_after": static_after,
        "pdf_path": OUTPUT_PDF_PATH
    }


def scrape_all_internships(driver):
    """Wrapper function for scraping internships"""
    return scrape_internships(driver)


if __name__ == "__main__":
    print(" Testing Internship Scraper...")
    driver= create_driver()
    result = scrape_internships(driver)

    print("Scraping completed")
    print(f"PDF Path: {result['pdf_path']}")
    print(f"Static Before Items: {len(result['static_before'])}")
    print(f"Dropdown Sections: {len(result['dropdowns'])}")

    for i, d in enumerate(result["dropdowns"], start=1):
        print(f"   {i}. {d['title']} → {len(d['content'])} items")

    print("Test finished successfully")
