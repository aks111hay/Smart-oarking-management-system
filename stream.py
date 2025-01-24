from flask import Flask, Response
import cv2

app = Flask(__name__)

# Replace with your ESP32-CAM's stream URL
ESP32_CAM_URL = "http://<ESP32_IP>:<PORT>/stream"  # Example: http://192.168.1.100:81/stream

def generate_frames():
    cap = cv2.VideoCapture(ESP32_CAM_URL)

    if not cap.isOpened():
        print("Error: Unable to open ESP32-CAM stream.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Unable to read frame from stream.")
            break

        # Encode the frame in JPEG format
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame as a byte stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
        <html>
            <head>
                <title>ESP32-CAM Video Stream</title>
            </head>
            <body>
                <h1>ESP32-CAM Video Stream</h1>
                <img src="/video" width="640" height="480">
            </body>
        </html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
