import cv2
import os
import numpy as np
import mediapipe as mp


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FACE_FOLDER = os.path.join(
    BASE_DIR,
    "ai_service",
    "registered_faces"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ai_service",
    "models",
    "blaze_face_short_range.tflite"
)


# ============================================================
# CHECK FOLDERS AND MODEL
# ============================================================

if not os.path.exists(FACE_FOLDER):
    print("ERROR: registered_faces folder not found.")
    print(FACE_FOLDER)
    exit()

if not os.path.exists(MODEL_PATH):
    print("ERROR: MediaPipe model not found.")
    print(MODEL_PATH)
    exit()

print("Face folder:")
print(FACE_FOLDER)

print("\nMediaPipe model:")
print(MODEL_PATH)


# ============================================================
# LOAD REGISTERED FACES
# ============================================================

faces = []
labels = []
student_names = {}

label_id = 0


for filename in os.listdir(FACE_FOLDER):

    if not filename.lower().endswith(
        (".jpg", ".jpeg", ".png")
    ):
        continue

    image_path = os.path.join(
        FACE_FOLDER,
        filename
    )

    image = cv2.imread(image_path)

    if image is None:
        print("Could not load:", filename)
        continue

    # Convert registered image to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Resize registered image
    gray = cv2.resize(
        gray,
        (200, 200)
    )

    faces.append(gray)

    # Filename becomes student ID
    student_id = os.path.splitext(
        filename
    )[0]

    labels.append(label_id)

    student_names[label_id] = student_id

    label_id += 1


# ============================================================
# CHECK REGISTERED STUDENTS
# ============================================================

print("\nRegistered students:")

for student_id in student_names.values():
    print("-", student_id)


if not faces:
    print("\nERROR: No registered faces found.")
    exit()


# ============================================================
# CREATE LBPH FACE RECOGNIZER
# ============================================================

recognizer = cv2.face.LBPHFaceRecognizer_create()

labels = np.array(
    labels,
    dtype=np.int32
)

recognizer.train(
    faces,
    labels
)

print("\nFace recognition model trained successfully.")


# ============================================================
# MEDIAPIPE FACE DETECTOR
# ============================================================

BaseOptions = mp.tasks.BaseOptions

FaceDetector = (
    mp.tasks.vision.FaceDetector
)

FaceDetectorOptions = (
    mp.tasks.vision.FaceDetectorOptions
)

VisionRunningMode = (
    mp.tasks.vision.RunningMode
)


detector_options = FaceDetectorOptions(

    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=VisionRunningMode.IMAGE,

    min_detection_confidence=0.5
)


# ============================================================
# START CAMERA
# ============================================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("\nERROR: Cannot open camera.")
    exit()


print("\nStarting camera...")
print("Camera started.")
print("Press Q to quit.")


# ============================================================
# FACE DETECTION + RECOGNITION
# ============================================================

with FaceDetector.create_from_options(
    detector_options
) as detector:

    while True:

        # ----------------------------------------------------
        # READ CAMERA FRAME
        # ----------------------------------------------------

        success, frame = camera.read()

        if not success:

            print(
                "Could not read camera."
            )

            break


        # ----------------------------------------------------
        # CONVERT BGR TO RGB
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # CREATE MEDIAPIPE IMAGE
        # ----------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        # ----------------------------------------------------
        # DETECT FACE
        # ----------------------------------------------------

        result = detector.detect(
            mp_image
        )


        # ----------------------------------------------------
        # IF FACE FOUND
        # ----------------------------------------------------

        if result.detections:

            for detection in result.detections:

                bbox = detection.bounding_box


                # ------------------------------------------------
                # GET FACE COORDINATES
                # ------------------------------------------------

                x = bbox.origin_x
                y = bbox.origin_y
                w = bbox.width
                h = bbox.height


                # ------------------------------------------------
                # KEEP COORDINATES INSIDE IMAGE
                # ------------------------------------------------

                x = max(
                    0,
                    x
                )

                y = max(
                    0,
                    y
                )

                w = min(
                    w,
                    frame.shape[1] - x
                )

                h = min(
                    h,
                    frame.shape[0] - y
                )


                # ------------------------------------------------
                # CROP FACE
                # ------------------------------------------------

                face = frame[
                    y:y + h,
                    x:x + w
                ]


                if face.size == 0:
                    continue


                # ------------------------------------------------
                # CONVERT FACE TO GRAYSCALE
                # ------------------------------------------------

                face_gray = cv2.cvtColor(
                    face,
                    cv2.COLOR_BGR2GRAY
                )


                # ------------------------------------------------
                # RESIZE FACE
                # ------------------------------------------------

                face_gray = cv2.resize(
                    face_gray,
                    (200, 200)
                )


                # ------------------------------------------------
                # RECOGNIZE FACE
                # ------------------------------------------------

                label, confidence = (
                    recognizer.predict(
                        face_gray
                    )
                )


                # ------------------------------------------------
                # GET STUDENT ID
                # ------------------------------------------------

                student_id = (
                    student_names[label]
                )


                # ------------------------------------------------
                # PRINT CONFIDENCE IN TERMINAL
                # ------------------------------------------------

                print(
                    f"Student: {student_id}, "
                    f"Confidence: {confidence:.2f}"
                )


                # ------------------------------------------------
                # RECOGNITION THRESHOLD
                #
                # LOWER LBPH SCORE = BETTER MATCH
                # ------------------------------------------------

                if confidence < 110:

                    text = (
                        f"{student_id} - Recognized"
                    )

                    box_color = (
                        0,
                        255,
                        0
                    )

                else:

                    text = (
                        "Unknown Face"
                    )

                    box_color = (
                        0,
                        0,
                        255
                    )


                # ------------------------------------------------
                # DRAW FACE BOX
                # ------------------------------------------------

                cv2.rectangle(

                    frame,

                    (x, y),

                    (x + w, y + h),

                    box_color,

                    2
                )


                # ------------------------------------------------
                # DISPLAY STUDENT / UNKNOWN
                # ------------------------------------------------

                cv2.putText(

                    frame,

                    text,

                    (
                        x,
                        max(
                            30,
                            y - 10
                        )
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.8,

                    box_color,

                    2
                )


                # ------------------------------------------------
                # DISPLAY SCORE
                # ------------------------------------------------

                cv2.putText(

                    frame,

                    f"Score: {confidence:.1f}",

                    (
                        x,
                        y + h + 25
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.6,

                    box_color,

                    2
                )


        # ========================================================
        # NO FACE DETECTED
        # ========================================================

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


        # ========================================================
        # QUIT INSTRUCTION
        # ========================================================

        cv2.putText(

            frame,

            "Q = Quit",

            (
                20,
                frame.shape[0] - 20
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 255),

            2
        )


        # ========================================================
        # SHOW CAMERA
        # ========================================================

        cv2.imshow(

            "SmartAttendAI - Face Recognition",

            frame
        )


        # ========================================================
        # PRESS Q TO QUIT
        # ========================================================

        if (
            cv2.waitKey(1) & 0xFF
        ) == ord("q"):

            break


# ============================================================
# STOP CAMERA
# ============================================================

camera.release()

cv2.destroyAllWindows()

print("\nCamera stopped.")