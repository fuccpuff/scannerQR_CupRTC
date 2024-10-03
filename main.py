from flask import Flask, request, jsonify, render_template_string, url_for
from datetime import datetime
import sqlite3
import logging

app = Flask(__name__)

# Путь к файлу базы данных
DB_FILE = 'qr_codes.db'

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    logging.info("База данных инициализирована.")

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
            logging.info(f"Получены данные QR-кода: {qr_data} в {timestamp}")
            return 'OK', 200
        else:
            logging.warning('Нет данных QR-кода в POST-запросе')
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
        logging.info('QR-коды получены для отображения.')
        return jsonify(qr_codes)

@app.route('/clear_qr_codes', methods=['POST'])
def clear_qr_codes():
    # Очищаем таблицу QR-кодов
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM qr_codes')
    conn.commit()
    conn.close()
    logging.info('QR-коды очищены.')
    return 'QR Codes Cleared', 200

@app.route('/')
def index():
    # Основная страница с отображением QR-кодов
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>QRobot</title>
        <link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet">
        <style>
            body {
                background-color: #f4f7f6;
            }
            .timestamp {
                font-size: 0.9rem;
                color: #6c757d;
            }
            .list-group-item {
                border: none;
                padding: 0;
            }
            .card:hover {
                transform: translateY(-5px);
                transition: transform 0.2s ease;
            }
            @media (max-width: 576px) {
                .btn-group {
                    flex-direction: column;
                    width: 100%;
                }
                .btn-group .btn {
                    width: 100%;
                    margin-bottom: 10px;
                }
                .btn-group .btn:last-child {
                    margin-bottom: 0;
                }
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">QRobot</a>
            </div>
        </nav>
        <div class="container my-5">
            <div id="alert_placeholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
                <h1 class="h3 mb-3 mb-md-0">Список считанных QR-кодов</h1>
                <div class="btn-group">
                    <button id="clear_btn" class="btn btn-danger">Очистить список</button>
                </div>
            </div>
            <ul id="qr_list" class="list-group">
                <!-- Данные будут динамически добавляться сюда -->
            </ul>
        </div>

        <script src="{{ url_for('static', filename='js/jquery.min.js') }}"></script>
        <script src="{{ url_for('static', filename='js/bootstrap.bundle.min.js') }}"></script>
        <script>
            var previousQrCount = 0;

            function fetchQrCodes() {
                $.ajax({
                    url: '/receive_qr',
                    type: 'GET',
                    success: function(data) {
                        // Проверяем, были ли добавлены новые QR-коды
                        if (data.length > previousQrCount) {
                            // Получен новый QR-код
                            showNotification('Новый QR-код получен!');
                            previousQrCount = data.length;
                        } else if (data.length < previousQrCount) {
                            // QR-коды были очищены
                            previousQrCount = data.length;
                        }

                        // Очищаем текущее содержимое
                        $('#qr_list').empty();
                        // Проходим по массиву QR-кодов и добавляем их в список
                        for (let i = 0; i < data.length; i++) {
                            let qrCode = data[i];
                            $('#qr_list').append(
                                '<li class="list-group-item mb-3">' +
                                    '<div class="card shadow-sm">' +
                                        '<div class="card-body">' +
                                            '<h5 class="card-title">' + (i + 1) + '. ' + qrCode.data + '</h5>' +
                                            '<p class="card-text timestamp">' + qrCode.timestamp + '</p>' +
                                        '</div>' +
                                    '</div>' +
                                '</li>'
                            );
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error('Ошибка при получении данных: ' + textStatus, errorThrown);
                    }
                });
            }

            function showNotification(message) {
                var alert = $(
                    '<div class="alert alert-success alert-dismissible fade show" role="alert">' +
                        message +
                        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                    '</div>'
                );
                $('#alert_placeholder').append(alert);

                // Удаляем уведомление через 5 секунд
                setTimeout(function() {
                    alert.alert('close');
                }, 5000);
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
                                previousQrCount = 0;
                                fetchQrCodes();
                            },
                            error: function(jqXHR, textStatus, errorThrown) {
                                console.error('Ошибка при очистке данных: ' + textStatus, errorThrown);
                            }
                        });
                    }
                });
            });
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
