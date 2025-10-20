from flask_bootstrap import Bootstrap
from flask import Flask, render_template, flash, request, redirect, url_for
from google.oauth2.service_account import Credentials
import datetime
import gspread
import random
import string


def generate_ticket_time():
    # Format timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    date, time = timestamp.split(" ")
    return date, time


def connect_google_sheet(worksheet_name, sheet_name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        ".creds/google_credentials.json",
        scopes=scope
    )
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
    respons = None
    alert_type = None
    try:
        if request.method == "POST":
            name = request.form["name"]
            phone = request.form["phone"]
            subject = request.form["subject"]
            message = request.form["message"]
            worksheet_name = "Daftar Pengaduan"
            sheet_name = "Data"

            save_to_sheet(worksheet_name, sheet_name, [name, phone, subject, message])

            respons = "✅ Data berhasil tersimpan!"
            alert_type = "success"
    except Exception as e:
        respons = f"❌ Gagal menyimpan data, silakan coba lagi. Error: {e}"
        alert_type = "danger"
    
    return render_template("contact.html", respons=respons, alert_type=alert_type)



if __name__ == '__main__':
    app.run()

