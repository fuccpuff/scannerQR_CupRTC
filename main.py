from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Путь к файлу базы данных
DB_FILE = 'qr_codes.db'

# Функция для инициализации базы данных
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Инициализация базы данных при запуске сервера
init_db()

@app.route('/receive_qr', methods=['GET', 'POST'])
def receive_qr():
    if request.method == 'POST':
        qr_data = request.form.get('qr_data')
        if qr_data:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO qr_codes (data, timestamp) VALUES (?, ?)', (qr_data, timestamp))
            conn.commit()
            conn.close()
            print(f"Received QR Data: {qr_data}")
            return 'OK', 200
        else:
            return 'No Data Received', 400
    elif request.method == 'GET':
        # Получаем все QR-коды из базы данных
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT data, timestamp FROM qr_codes')
        rows = cursor.fetchall()
        conn.close()

        qr_codes = []
        for row in rows:
            qr_codes.append({
                'data': row[0],
                'timestamp': row[1]
            })
        return jsonify(qr_codes)

@app.route('/clear_qr_codes', methods=['POST'])
def clear_qr_codes():
    # Очищаем таблицу QR-кодов
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM qr_codes')
    conn.commit()
    conn.close()
    return 'QR Codes Cleared', 200

@app.route('/')
def index():
    # Основная страница с отображением QR-кодов
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QR Code Scanner</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body {
                background-color: #f4f7f6;
                font-family: 'Arial', sans-serif;
            }
            .container {
                max-width: 900px;
                margin-top: 50px;
            }
            h1 {
                font-size: 2.5rem;
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }
            .list-group-item {
                background-color: #fff;
                border: none;
                border-radius: 8px;
                margin-bottom: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease;
            }
            .list-group-item:hover {
                transform: translateY(-5px);
            }
            .timestamp {
                font-size: 0.9rem;
                color: #6c757d;
            }
            .btn-clear {
                margin-bottom: 20px;
                background-color: #ff6b6b;
                color: white;
                border: none;
                transition: background-color 0.3s ease;
            }
            .btn-clear:hover {
                background-color: #ff4c4c;
            }
            footer {
                text-align: center;
                margin-top: 50px;
                font-size: 0.9rem;
                color: #999;
            }
        </style>
        <script type="text/javascript">
            function fetchQrCodes() {
                $.ajax({
                    url: '/receive_qr',
                    type: 'GET',
                    success: function(data) {
                        // Очищаем текущее содержимое
                        $('#qr_list').empty();
                        // Проходим по массиву QR-кодов и добавляем их в список
                        for (let i = 0; i < data.length; i++) {
                            let qrCode = data[i];
                            $('#qr_list').append(
                                '<li class="list-group-item">' +
                                '<strong>' + (i + 1) + '. ' + qrCode.data + '</strong><br>' +
                                '<span class="timestamp">' + qrCode.timestamp + '</span>' +
                                '</li>'
                            );
                        }
                    }
                });
            }

            // Обновляем данные каждые 5 секунд
            setInterval(fetchQrCodes, 5000);

            // Обновляем данные при загрузке страницы
            $(document).ready(function(){
                fetchQrCodes();

                $('#clear_btn').click(function(){
                    if(confirm('Вы уверены, что хотите очистить список QR-кодов?')) {
                        $.ajax({
                            url: '/clear_qr_codes',
                            type: 'POST',
                            success: function() {
                                fetchQrCodes();
                            }
                        });
                    }
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Список считанных QR-кодов</h1>
            <button id="clear_btn" class="btn btn-clear">Очистить список</button>
            <ul id="qr_list" class="list-group">
                <!-- Данные будут динамически добавляться сюда -->
            </ul>
        </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
