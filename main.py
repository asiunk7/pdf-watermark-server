from flask import Flask, request, send_file, abort
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

app = Flask(__name__)

@app.route('/')  # 🟢 ROUTE ANTI-SLEEP
def keep_alive():
    return 'Server aktif bro 👊', 200

@app.route('/ping')  # 🟢 Route ringan buat UptimeRobot
def ping():
    return 'pong', 200

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

        # ✅ Tambahkan watermark di tengah halaman
        can.saveState()
        can.translate(300, 400)  # posisi tengah halaman (x=300, y=400)
        can.rotate(45)           # kemiringan watermark
        can.setFont("Helvetica-Bold", 40)
        can.setFillGray(0.5, 0.1)  # warna abu-abu terang dengan transparansi
        can.drawCentredString(0, 20, "Downloaded by")
        can.drawCentredString(0, -20, name)
        can.restoreState()

        can.save()
        packet.seek(0)

        watermark = PdfReader(packet)
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name=f"watermarked_{filename}", mimetype='application/pdf')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
