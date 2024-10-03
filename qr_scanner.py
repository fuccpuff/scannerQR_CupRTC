import cv2
from pyzbar import pyzbar
import threading
import time
from flask import Flask, Response
import requests

def initialize_camera():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open video device")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cap
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

class QRCodeScanner:
    def __init__(self):
        self.cap = initialize_camera()
        self.frame = None

    def scan(self):
        last_qr_data = None
        while True:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                self.frame = frame.copy()
                decoded_objects = pyzbar.decode(frame)

                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    if qr_data != last_qr_data:
                        print(f"Detected QR Code: {qr_data}")
                        self.send_data(qr_data)
                        last_qr_data = qr_data

                    (x, y, w, h) = obj.rect
                    cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(self.frame, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 0), 2)

                time.sleep(0.1)
            except Exception as e:
                print(f"Error during scanning: {e}")
                break

    def send_data(self, data):
        url = 'http://ip_address:port/receive_qr'
        try:
            response = requests.post(url, data={'qr_data': data})
            if response.status_code == 200:
                print("Data sent successfully")
            else:
                print(f"Failed to send data, status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")

    def release(self):
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()

app = Flask(__name__)
scanner = QRCodeScanner()

def gen_frames():
    while True:
        if scanner.frame is not None:
            ret, buffer = cv2.imencode('.jpg', scanner.frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/')
def index():
    return "QR Code Scanner is running. View the video stream at /video_feed"

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def start_scanner():
    scanner.scan()

if __name__ == '__main__':
    try:
        scanner_thread = threading.Thread(target=start_scanner)
        scanner_thread.daemon = True
        scanner_thread.start()

        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        scanner.release()
