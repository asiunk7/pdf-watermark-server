from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
import uuid

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
        can.translate(300, 400)
        can.rotate(45)
        can.setFont("Helvetica-Bold", 40)
        can.setFillGray(0.5, 0.1)
        can.drawCentredString(0, 20, "Downloaded by")
        can.drawCentredString(0, -20, name)
        can.restoreState()
        can.save()
        packet.seek(0)

        watermark = PdfReader(packet)
        page.merge_page(watermark.pages[0])
        writer.add_page(page)

    # ✅ Simpan ke file sementara
    temp_filename = f"temp_{uuid.uuid4().hex}.pdf"
    temp_filepath = os.path.join("pdfs", temp_filename)

    with open(temp_filepath, "wb") as f:
        writer.write(f)

    # ✅ Kirim file sebagai download
    response = send_file(temp_filepath, as_attachment=True,
                         download_name=f"APIC_{filename}",
                         mimetype='application/pdf')

    # ✅ Hapus file setelah response selesai dikirim
    @response.call_on_close
    def cleanup():
        try:
            os.remove(temp_filepath)
        except:
            pass

    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
