import cv2
import mediapipe as mp

MODEL_PATH = "ai_service/models/blaze_face_short_range.tflite"

# MediaPipe Tasks
BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
RunningMode = mp.tasks.vision.RunningMode


# Configure face detector
options = FaceDetectorOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=RunningMode.VIDEO,
    min_detection_confidence=0.5
)


# Open camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Camera could not be opened")
    exit()

print("✅ Camera opened successfully")
print("🤖 MediaPipe face detector started")
print("Press Q to close.")


with FaceDetector.create_from_options(options) as detector:

    frame_timestamp_ms = 0

    while True:

        success, frame = camera.read()

        if not success:
            print("❌ Could not read camera frame")
            break

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Convert to MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Detect faces
        result = detector.detect_for_video(
            mp_image,
            frame_timestamp_ms
        )

        frame_timestamp_ms += 33

        # Draw results
        if result.detections:

            for detection in result.detections:

                bbox = detection.bounding_box

                x = bbox.origin_x
                y = bbox.origin_y
                width = bbox.width
                height = bbox.height

                # Draw face rectangle
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (0, 255, 0),
                    2
                )

                # Confidence
                score = detection.categories[0].score

                cv2.putText(
                    frame,
                    f"Face Detected: {score:.2f}",
                    (x, max(y - 10, 30)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        else:

            cv2.putText(
                frame,
                "No Face Detected",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # Show camera
        cv2.imshow(
            "SmartAttendAI - Face Detection",
            frame
        )

        # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


camera.release()
cv2.destroyAllWindows()