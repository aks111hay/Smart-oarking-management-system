# Smart Parking Flask App

This project is a **Smart Parking Flask Application** designed to automate parking management by detecting license plates and suggesting available slots. It uses a YOLOv8-based license plate detection model for object detection, making parking management more efficient and organized. Contributions are welcomed to improve its performance and functionality.

---

## Features

1. **Automatic License Plate Detection**:
   - Utilizes the YOLOv8 model for license plate recognition.
   - Detects license plates in real-time from video streams or uploaded videos.

2. **Parking Slot Management**:
   - Identifies empty slots by analyzing video frames.
   - Suggests available slots to optimize parking allocation based on detected empty spaces.
   - Dynamically updates the availability status in real-time.

3. **User Management**:
   - Users can register and log in to manage their parking slots.
   - Provides a dashboard for administrators to monitor parking activity.

4. **Database Integration**:
   - Stores detected license plate information, timestamps, and parking slot status in the database for record-keeping.

---

## Installation and Setup

### Prerequisites
Ensure the following are installed on your system:
- Python (>= 3.8)
- Flask
- OpenCV
- Pytesseract
- YOLOv8
- Virtual environment (optional but recommended)

### Steps to Set Up

1. **Clone the Project Repository**:
   - Ensure your Flask app includes the following files:
     - `app.py`: Main Flask application.
     - `models.py`: Database models.
     - `requirements.txt`: List of dependencies.

2. **Create a Virtual Environment (Optional)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Tesseract OCR**:
   - Download and install Tesseract OCR from [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract).
   - Update the `tesseract_cmd` path in your code:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
     ```

5. **Run the Flask Application**:
   ```bash
   flask run
   ```
   The app will be available at: `http://127.0.0.1:5000`

---

## Usage

1. **Register and Login**:
   - Create an account to access the application.
   - Log in to view your dashboard.

2. **Upload Video**:
   - Upload a video containing parking lot footage.
   - The system will automatically detect license plates and analyze parking availability.

3. **Available Slot Suggestions**:
   - Based on detected empty slots, the system suggests available parking spaces.
   - Real-time updates ensure accurate availability status for users.

4. **View Logs**:
   - Admins can monitor detected license plates, parking activity, and timestamp records via the dashboard.

---

## Limitations

- **Detection Accuracy**:
  - The model might not detect plates efficiently in low-light or cluttered environments.
- **Performance**:
  - Processing speed and accuracy depend on the video quality and system resources.

---

## Contributions

Contributions are encouraged to make this application more efficient and feature-rich. Here’s how you can contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---

## License
This project is open-source and available under the MIT License.

---

## Acknowledgments

Special thanks to [Muhammad Zeerak Khan](https://github.com/Muhammad-Zeerak-Khan) for the YOLOv8-based license plate detection model that inspired this application.

