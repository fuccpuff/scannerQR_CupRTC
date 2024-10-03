# QR Code Scanner Project

## Описание

Это проект для автоматического сканирования QR-кодов с помощью камеры Raspberry Pi и отправки данных на сервер, расположенный на ПК. Сервер сохраняет данные QR-кодов в базе данных SQLite и отображает их через веб-интерфейс. Также есть возможность очистки списка считанных QR-кодов через веб-интерфейс. Программа состоит из двух скриптов: один запускается на Raspberry Pi для сканирования QR-кодов, другой — на ПК для приема данных и их отображения.

## Требования

### Для Raspberry Pi:
- Python 3.x
- OpenCV
- Pyzbar
- Flask
- Requests

### Для ПК:
- Python 3.x
- Flask
- SQLite

## Установка и настройка

### 1. Raspberry Pi

1. Установите Python и необходимые зависимости:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv libopencv-dev python3-opencv
2. Создайте виртуальное окружение и установите необходимые библиотеки:
    ```bash
   python3 -m venv ~/myenv
   source ~/myenv/bin/activate
   pip install opencv-python pyzbar flask requests
3. Запустите скрипт для сканирования QR-кодов
    ```bash
   source ~/myenv/bin/activate
   python qr_scanner.py

### 2. ПК

1. Установите Python и необходимые библиотеки
    ```bash
   sudo apt-get install python3 python3-pip
   pip install flask sqlite3
2. Создайте базу данных и запустите сервер
    ```bash
   python pc_server.py
   
## Автоматический запуск на Raspberry Pi

Чтобы скрипт на Raspberry Pi запускался автоматически при включении:

1. Откройте crontab:
   ```bash
   crontab -e
2. Добавьте следующую строку для автозапуска скрипта:
    ```bash
   @reboot /bin/bash -c "source /home/pi/myenv/bin/activate && python /home/pi/qr_scanner.py"

### Использование

1. Убедитесь, что Raspberry Pi и ПК подключены к одной сети.
2. Запустите скрипт на Raspberry Pi для сканирования QR-кодов.
3. Запустите сервер на ПК для приема и отображения данных.
4. Откройте веб-браузер и перейдите по адресу http://<IP_адрес_ПК>:5000, чтобы просмотреть список считанных QR-кодов и очистить его при необходимости.

### Примечание

Все данные QR-кодов сохраняются в базу данных SQLite на ПК, чтобы избежать потери данных при перезапуске или сбоях сервера.