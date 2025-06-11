from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

app = Flask(__name__)

@app.route('/generate')
def generate_pdf():
    name = request.args.get('name', 'Unknown User')

    # Load base PDF
    reader = PdfReader("template.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 10)
        can.drawString(50, 30, f"Downloaded by {name}")
        can.save()
        packet.seek(0)

        # Merge watermark
        watermark = PdfReader(packet)
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="watermarked.pdf", mimetype='application/pdf')
