from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import os
def generate_internship_pdf(text_data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        spaceAfter=10,
        leading=14
    )

    story = []

    # ---------------- Title ----------------
    story.append(Paragraph("Internship Information", title_style))
    story.append(Spacer(1, 20))

    # ---------------- Content ----------------
    for text in text_data:
        story.append(Paragraph(text, body_style))

    doc.build(story)
