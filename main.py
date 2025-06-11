from flask import Flask, request, send_file, abort
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

app = Flask(__name__)

@app.route('/generate')
def generate_pdf():
    name = request.args.get('name', 'Unknown User')
    filename = request.args.get('filename', None)

    if not filename:
        return "Missing filename", 400

    file_path = os.path.join("pdfs", filename)

    if not os.path.isfile(file_path):
        return "File not found", 404

    reader = PdfReader(file_path)
    writer = PdfWriter()

    for page in reader.pages:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 10)
        can.drawString(50, 30, f"Downloaded by {name}")
        can.save()
        packet.seek(0)

        watermark = PdfReader(packet)
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name=f"watermarked_{filename}", mimetype='application/pdf')
