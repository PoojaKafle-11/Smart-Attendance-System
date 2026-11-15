import cv2
import mediapipe as mp
import os

# -----------------------------
# Settings
# -----------------------------
MODEL_PATH = "ai_service/models/blaze_face_short_range.tflite"
SAVE_FOLDER = "ai_service/registered_faces"

# Create folder if it doesn't exist
os.makedirs(SAVE_FOLDER, exist_ok=True)

# -----------------------------
# MediaPipe setup
# -----------------------------
BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    min_detection_confidence=0.5
)

# -----------------------------
# Ask for student ID
# -----------------------------
student_id = input("Enter Student ID: ").strip()

if not student_id:
    print("Student ID cannot be empty.")
    exit()

# -----------------------------
# Open camera
# -----------------------------
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open camera.")
    exit()

print("\nCamera started.")
print("Press S to save the face.")
print("Press Q to quit.")

with FaceDetector.create_from_options(options) as detector:

    while True:

        success, frame = camera.read()

        if not success:
            print("Failed to read camera frame.")
            break

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Detect faces
        result = detector.detect(mp_image)

        # Draw detected faces
        if result.detections:

            for detection in result.detections:

                bbox = detection.bounding_box

                x = bbox.origin_x
                y = bbox.origin_y
                w = bbox.width
                h = bbox.height

                # Draw rectangle
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                # Confidence
                confidence = detection.categories[0].score

                cv2.putText(
                    frame,
                    f"Face: {confidence:.2f}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        else:

            cv2.putText(
                frame,
                "No face detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # Instructions
        cv2.putText(
            frame,
            "Press S = Save | Q = Quit",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.imshow("SmartAttendAI - Face Registration", frame)

        key = cv2.waitKey(1) & 0xFF

        # Save face
        if key == ord("s"):

            if result.detections:

                filename = os.path.join(
                    SAVE_FOLDER,
                    f"{student_id}.jpg"
                )

                cv2.imwrite(filename, frame)

                print(f"\nFace saved successfully!")
                print(f"File: {filename}")

            else:

                print("\nNo face detected. Please position your face in front of the camera.")

        # Quit
        elif key == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()

print("\nCamera stopped.")