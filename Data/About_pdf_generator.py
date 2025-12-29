from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import textwrap


def generate_internship_pdf(internship_sections):
    output_path = r"D:\SUNBEAM PROJECT\IIT-GENAI-PROJECT-SUNBEAM_CHATBOT\Data\internship_data.pdf"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    x_margin = 1 * inch
    y_margin = 1 * inch

    text_obj = pdf.beginText(x_margin, height - y_margin)

    text_obj.setFont("Helvetica-Bold", 16)
    text_obj.textLine("Internship Program")
    text_obj.textLine("")

    for section_title, section_content in internship_sections.items():
        if not section_content:
            continue

        text_obj.setFont("Helvetica-Bold", 12)
        text_obj.textLine(section_title)
        text_obj.textLine("")

        text_obj.setFont("Helvetica", 11)

        for paragraph in section_content.split("\n\n"):
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
