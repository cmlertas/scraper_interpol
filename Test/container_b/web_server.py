from flask import Flask, render_template, request
from pymongo import MongoClient
import datetime
import pytz
import math  
'''
Flask ile basit bir web servisi kurulur,veri tabanı ile bağlantı kurularak veriler liste olarak işlenir ordan  
html sayfasına işlenir, her bir sayfada 20 tane veri olacak şekilde ayarlanmıştır.
Son güncelleme saati veritabanından web sitesine işlenen verinin zamanıdır.Web sitesi localhost:5000 de bulunur.
'''
app = Flask(__name__)
client = MongoClient('mongodb://mongo:27017/')  # Mongo bağlantısı

db = client['interpol_database']  # Veritabanı adı

# Zaman bilgisini al
def get_update_time():
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    current_time = datetime.datetime.now(istanbul_tz)
    return current_time.strftime("%Y-%m-%d %H:%M:%S")

# Ana sayfa
@app.route('/')
def show_data():
    page = request.args.get('page', default=1, type=int)  
    items_per_page = 20  # Sayfadaki öğe sayısı

    interpol_data_cursor = db.interpol_data.find().skip((page - 1) * items_per_page).limit(items_per_page)  # Veritabanından veriyi çek

    
    interpol_data = list(interpol_data_cursor)

    total_items = db.interpol_data.count_documents({})  # Toplam veri sayısı
    total_pages = math.ceil(total_items / items_per_page)  # Toplam sayfa sayısı

    update_time = get_update_time()
    return render_template('index.html', data=interpol_data, update_time=update_time, current_page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
