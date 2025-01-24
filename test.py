import os
import cv2
import pytesseract
from ultralytics import YOLO
from datetime import datetime

# Initialize YOLO model
model = YOLO('license_plate_detector.pt')  

# Path to Tesseract executable (adjust according to your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
def process_video(video_path):
    """Process video to detect number plates."""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    print(f"Processing video: {video_path}")
    
    detected_plates = []
    empty_frames_count = 0  # Counter for empty frames
    
    while cap.isOpened():
        ret,frame = cap.read()
        if not ret:
            break 
        frame = cv2.resize(frame, (1300, 1300))  

        # Detect objects in the frame using YOLO model
        results = model(frame)

        frame_has_plate = False  # Flag to check if current frame has a plate
        if not results[0].boxes:  # No bounding boxes detected
            empty_frames_count += 1
            print("Empty frame detected.")
            continue
        
        
    
        for result in results:
            for box in result.boxes:  # YOLO bounding boxes
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Convert bounding box coordinates
                conf = box.conf[0].item()  # Confidence score

                if conf > 0.5:  # Confidence threshold
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  
                    # Extract the region of interest (ROI) for the number plate
                    roi = frame[y1:y2, x1:x2]

                    # Preprocess the image for better OCR accuracy
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
                    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # Thresholding

                    # Perform OCR to detect number plate text
                    plate_text = pytesseract.image_to_string(thresh, config='--psm 8').strip()
                    
                    if plate_text:
                        now = datetime.now()
                        detected_plates.append((plate_text, now))
                        print(f"Detected Plate: {plate_text} at {now}")
                        frame_has_plate = True  # Mark that plate was detected in this frame
        
        if not frame_has_plate:
            empty_frames_count += 1  # Increment empty frames count
            cv2.imshow("available slots is ",empty_frames_count)
            print(f"available slots is {empty_frames_count}")
        
        # Display the frame with bounding boxes for debugging (optional)
        cv2.imshow("Detected Plates", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to stop
            break

    cap.release()
    cv2.destroyAllWindows()
    
    # Print number of empty frames
    print(f"\nNumber of Empty Frames: {empty_frames_count}")
    
    # Print all detected plates
    print("\nFinal Detected Plates:")
    for plate, time in detected_plates:
        print(f"Plate: {plate}, Time: {time}")

    return detected_plates

if __name__ == "__main__":
    # Replace this with the path to your test video
    video_path = r"C:\Users\AKSHAY KUMAR\Documents\projects\parkmaster\static\number_plate.mp4"
    if not os.path.exists(video_path):
        print(f"Error: File not found at {video_path}")
    else:
        detected_plates = process_video(video_path)
        # print(detected_plates)