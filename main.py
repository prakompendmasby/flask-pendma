from dotenv import load_dotenv
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, flash, request, redirect, url_for
from google.oauth2.service_account import Credentials
import datetime
import gspread
import json
import os
import random
import string


def generate_ticket_code():
    # Format timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d#%H%M%S#%f#%a").upper()
    
    # Random uppercase letters
    random_letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
    
    # Combine with #
    return f"{timestamp}#{random_letters}"


def connect_google_sheet(worksheet_name, sheet_name):

    load_dotenv()
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(creds_json)

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    # creds = Credentials.from_service_account_file(
    #     ".creds/google_credentials.json",
    #     scopes=scope
    # )
    client = gspread.authorize(creds)
    # sheet = client.open(sheet_name).sheet1   # open the first worksheet
    worksheet = client.open(worksheet_name).worksheet(sheet_name)  # pilih tab bernama "Data"
    return worksheet


def save_to_sheet(worksheet_name, sheet_name, data):
    sheet = connect_google_sheet(worksheet_name, sheet_name)

    now = datetime.datetime.now()
    row_data = [now.strftime("%Y/%m/%d"), now.strftime("%H:%M:%S")] + data
    # masukkan di baris ke-2 (tepat di bawah header)
    sheet.insert_row(row_data, 2, value_input_option="USER_ENTERED")
    # sheet.append_row(row_data)
    print(f"Saved to sheet: {row_data}")


def get_data_by_column(worksheet_name, sheet_name, column_name, value_search):
    sheet = connect_google_sheet(worksheet_name, sheet_name)
    records = sheet.get_all_records()  # list of dict

    for row in records:
        if str(row.get(column_name)).strip().lower() == str(value_search).strip().lower():
            return row

    return None



def create_app():
  app = Flask(__name__)
  Bootstrap(app)
  return app


app = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    page_type = "view"
    respons = None
    alert_type = None
    try:
        if request.method == "POST":
            ticket_code = generate_ticket_code()
            name = request.form["name"]
            phone = request.form["phone"]
            subject = request.form["subject"]
            message = request.form["message"]
            status = "Proses"
            worksheet_name = "Daftar Pengaduan"
            sheet_name = "Data"

            save_to_sheet(worksheet_name, sheet_name, [ticket_code, name, phone, subject, message, status])

            page_type = "ticket"
            respons = "✅ Data berhasil tersimpan!"
            alert_type = "success"

            return render_template("contact/contact.html", respons=respons, alert_type=alert_type, page_type=page_type, ticket_code=ticket_code)
    except Exception as e:
        respons = f"❌ Gagal menyimpan data, silakan coba lagi. Error: {e}"
        alert_type = "danger"
    
    return render_template("contact/contact.html", respons=respons, alert_type=alert_type, page_type=page_type)


@app.route('/contact-check', methods=['GET', 'POST'])
def contact_check():
    page_type = "view"
    respons = None
    alert_type = None
    try:
        if request.method == "POST":
            ticket_code = request.form["ticket-code"]
            worksheet_name = "Daftar Pengaduan"
            sheet_name = "Data"
            column_name = "Kode Tiket"

            hasil = get_data_by_column(worksheet_name, sheet_name, column_name, ticket_code)

            if hasil:
                respons = hasil
                alert_type = "success"
                page_type = "ticket"
                return render_template("contact/contact-check.html", respons=respons, alert_type=alert_type, page_type=page_type, ticket_code=ticket_code)
            else:
                respons = f"❌ Tidak ada data dengan kode tiket {ticket_code}"
                alert_type = "danger"
                return render_template("contact/contact-check.html", respons=respons, alert_type=alert_type, page_type=page_type, ticket_code=ticket_code)
    except Exception as e:
        respons = f"❌ Gagal mencari data, silakan coba lagi. Error: {e}"
        alert_type = "danger"
    
    return render_template('contact/contact-check.html', respons=respons, alert_type=alert_type, page_type=page_type)


@app.route('/information')
def information():
    return render_template('information/information.html')


@app.route('/information-read/', defaults={'title': None})
@app.route('/information-read/<title>')
def information_read(title):
    content = None  # default
    if title is not None:
        try:
            with open(f"templates/information-txt/{title}.txt", "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = None
    
    return render_template(
        'information/information-read.html',
        title=title.replace('_', ' ') if title else None,
        content=content
    )


@app.route('/struktur-kemenag')
def struktur_kemenag():
    return render_template('profil/struktur-kemenag.html')


@app.route('/visi-misi')
def visi_misi():
    return render_template('profil/visi-misi.html')


@app.route('/tugas-fungsi')
def tugas_fungsi():
    return render_template('profil/tugas-fungsi.html')



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



