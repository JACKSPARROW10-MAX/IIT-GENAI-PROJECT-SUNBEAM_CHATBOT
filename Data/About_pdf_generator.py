from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import textwrap


def generate_about_us_pdf(section_1, section_2):
    output_path = r"D:\SUNBEAM PROJECT\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\about_us.pdf"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    x_margin = 1 * inch
    y_margin = 1 * inch

    text_obj = pdf.beginText(x_margin, height - y_margin)

    # ---------------- Title ----------------
    text_obj.setFont("Helvetica-Bold", 16)
    text_obj.textLine("About Us")
    text_obj.textLine("")

    # ---------------- Section 1 ----------------
    text_obj.setFont("Helvetica-Bold", 12)
    text_obj.textLine("Section 1: About Institute")
    text_obj.textLine("")

    text_obj.setFont("Helvetica", 11)
    for paragraph in section_1:
        wrapped_lines = textwrap.wrap(paragraph, 90)
        for line in wrapped_lines:
            if text_obj.getY() < y_margin:
                pdf.drawText(text_obj)
                pdf.showPage()
                text_obj = pdf.beginText(x_margin, height - y_margin)
                text_obj.setFont("Helvetica", 11)
            text_obj.textLine(line)
        text_obj.textLine("")

    # ---------------- Section 2 ----------------
    text_obj.setFont("Helvetica-Bold", 12)
    text_obj.textLine("Section 2: Additional Information")
    text_obj.textLine("")

    text_obj.setFont("Helvetica", 11)
    for paragraph in section_2:
        wrapped_lines = textwrap.wrap(paragraph, 90)
        for line in wrapped_lines:
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
