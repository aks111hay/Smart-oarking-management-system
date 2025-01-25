import os
import cv2
import time
import pytesseract
from werkzeug.utils import secure_filename
from datetime import datetime
from ultralytics import YOLO
from flask import Flask, request, redirect, url_for, render_template, flash,Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import session
import torch
import pytesseract

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows path


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parkmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')  # Absolute path to 'uploads' directory
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit file size to 50MB
app.config['SECRET_KEY'] = 'ASDGFDTG'  # Set a strong secret key

bcrypt = Bcrypt(app)
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
from model import *
db.init_app(app)

# Initialize YOLO model (adjust model path if needed)
model = YOLO('license_plate_detector.pt')

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
UPLOAD_FOLDER = "./uploads"
ESP32_CAM_URL = "" 
@app.route('/set_stream_url', methods=['POST'])
def set_stream_url():
    """Set the URL for the ESP32-CAM stream."""
    global ESP32_CAM_URL
    data = request.get_json()
    if 'url' not in data:
        return {"error": "No URL provided"}, 400
    ESP32_CAM_URL = data['url']
    return {"message": "ESP32-CAM URL updated successfully!"}, 200


@app.route('/process_live', methods=['POST'])
def process_live_stream():
    """Capture live video from ESP32-CAM, save a short video, and process it."""
    if not ESP32_CAM_URL:
        return {"error": "ESP32-CAM URL not set. Please use /set_stream_url first."}, 400

    cap = cv2.VideoCapture(ESP32_CAM_URL)
    if not cap.isOpened():
        return {"error": "Failed to connect to ESP32-CAM stream. Check the URL."}, 500

    # Capture live video frames and save them temporarily
    frame_count = 0
    video_filename = os.path.join(UPLOAD_FOLDER, f"live_capture_{int(time.time())}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for AVI file
    fps = 10  # Frames per second for the saved video
    frame_size = (640, 480)  # Adjust based on ESP32-CAM resolution
    out = cv2.VideoWriter(video_filename, fourcc, fps, frame_size)

    start_time = time.time()
    while time.time() - start_time < 10:  # Record for 10 seconds
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Stopping...")
            break
        frame_count += 1
        out.write(frame)

    cap.release()
    out.release()

    # Call your existing upload_video and process_video functions
    print(f"Captured video saved at: {video_filename}")
    upload_video(video_filename)  # Replace with your upload function
    process_video(video_filename)  # Replace with your process function

    return {"message": "Live stream processed successfully!"}, 200

#Function to process video and detect number plates
def process_video(video_path, model):
    """Process video to detect number plates and log results."""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}.")
        return

    print(f"Processing video: {video_path}")
    frame_count = 0
    frame_skip = 5  # Skip every 5th frame for efficiency

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # Skip frames to improve performance

        # Resize frame for consistent YOLO processing (optional)
        frame = cv2.resize(frame, (1300, 1300))

        # Run YOLO inference
        results = model(frame)
        
        if not results[0].boxes:  # No bounding boxes detected
            empty_frames_count += 1
            print("Empty frame detected.")
            continue

        # Process detected objects
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box coordinates
            conf = box.conf[0].item()  # Confidence score
            cls = int(box.cls[0].item())  # Class index
            class_name = results[0].names[cls]  # Class name

            # Check if the detected object is a license plate
            if class_name == "license_plate":  
                print(f"Detected {class_name} with confidence {conf:.2f} at [{x1}, {y1}, {x2}, {y2}]")

                # Extract the region of interest (ROI) for the number plate
                roi = frame[y1:y2, x1:x2]

                # Preprocess the ROI for OCR
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                # Perform OCR to extract text
                plate_text = pytesseract.image_to_string(thresh, config="--psm 8").strip()
                if plate_text:
                    
                    now = datetime.now()
                    print(f"Detected Plate: {plate_text} at {now}")

                        # Draw bounding box and text on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, plate_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # Update the database with detected plate
                    try:
                            # Check if the plate is already in the database (entry without exit time)
                            existing_entry = ParkingData.query.filter_by(number_plate=plate_text, exit_time=None).first()

                            if existing_entry:
                                # Update the exit time for the existing entry
                                existing_entry.exit_time = now
                                print(f"Updated exit time for plate: {plate_text}")
                            else:
                                # Add a new entry for the detected plate
                                new_entry = ParkingData(number_plate=plate_text, entry_time=now, parking_lot_id=1)
                                db.session.add(new_entry)
                                print(f"Added new entry for plate: {plate_text}")

                            # Commit changes to the database
                            db.session.commit()
                            print("Database updated successfully!")

                    except Exception as e:
                            db.session.rollback()
                            print(f"Database error: {e}")
                else:
                    print(f"availiable parking slots {frame_count}")

        # Display the frame with detections (optional)
        cv2.imshow("Number Plate Detection", frame)
        cv2.imshow("availiable slots",{empty_frames_count})
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Video processing completed.")

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        flash('No video file selected', 'error')
        return redirect(url_for('dashboard'))

    file = request.files['video']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard'))

    if file:
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)

        # Process the uploaded video within an app context
        try:
            with app.app_context():
                process_video(video_path,model)
                flash('Video processed successfully!', 'success')
        except Exception as e:
            flash(f'Error processing video: {e}', 'error')

        return redirect(url_for('dashboard'))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    # Fetch user and parking lot data
    user = User.query.filter_by(email=session['user']).first()
    parking_lot = ParkingLot.query.first()
    cars_in_parking = ParkingData.query.filter_by(exit_time=None).count()

    # Calculate parking availability percentage
    parking_availability = (parking_lot.capacity - cars_in_parking) 

    return render_template(
        'dashboard.html',
        user=user,
        cars_in_parking=cars_in_parking,
        parking_availability=parking_availability
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        # Authenticate user
        if user and bcrypt.check_password_hash(user.password, password):
            session['user'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if the user already exists
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return redirect(url_for('register'))

        # Find a parking lot with available capacity
        parking_lot = ParkingLot.query.filter(
            db.func.count(ParkingLot.users) < ParkingLot.capacity
        ).first()

        if not parking_lot:
            flash('No available parking lots at the moment. Please try again later.', 'danger')
            return redirect(url_for('register'))

        # Create and save the new user
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            parking_lot_id=parking_lot.id
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('register'))

    return render_template('registration.html')


@app.route('/summary')
def summary():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    # Fetch the user based on the session email
    user = User.query.filter_by(email=session['user']).first_or_404()  # Fetch the logged-in user

    # Get the user's associated parking lot
    parking_lot = ParkingLot.query.get(user.parking_lot_id)  # Fetch the parking lot associated with the user

    if not parking_lot:
        flash('Parking lot not found.', 'danger')
        return redirect(url_for('dashboard'))

    # Fetch parking summary data for the user's parking lot
    total_vehicles = ParkingData.query.filter_by(parking_lot_id=parking_lot.id).count()  # Total vehicles in the user's parking lot
    cars_in_parking = ParkingData.query.filter_by(parking_lot_id=parking_lot.id, exit_time=None).count()  # Cars still in the parking lot
    available_spaces = (parking_lot.capacity - cars_in_parking)  # Available spaces based on parking lot capacity

    # Fetch recent parking data for the user's parking lot
    recent_records = ParkingData.query.filter_by(parking_lot_id=parking_lot.id).order_by(ParkingData.entry_time.desc()).limit(10).all()

    return render_template(
        'summary.html',
        total_vehicles=total_vehicles,
        available_spaces=available_spaces,
        recent_records=recent_records,
        parking_lot=parking_lot
    )


@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    search_results = None
    if request.method == 'POST':
        number_plate = request.form.get('search')
        search_date = request.form.get('date')

        # Perform search queries
        query = ParkingData.query
        if number_plate:
            query = query.filter(ParkingData.number_plate.contains(number_plate))
        if search_date:
            query = query.filter(ParkingData.entry_time.like(f'{search_date}%'))

        search_results = query.all()

    return render_template('search.html', results=search_results)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))



# Run the app
if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
