

import os
import sys
import cv2
import numpy as np
import django

from pathlib import Path
from insightface.app import FaceAnalysis

# =========================================
# 1. DJANGO SETUP
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Add the main project directory to Python's import path
sys.path.insert(0, str(BASE_DIR))

# Configure Django settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

# Initialize Django
django.setup()

# Import Django models after initialization
from students.models import Student
from attendance.models import AttendanceSession, Attendance
from django.utils import timezone

# =========================================
# 2. PATHS
# =========================================

EMBEDDING_FOLDER = os.path.join(
    BASE_DIR,
    "ai_service",
    "face_embeddings"
)


# =========================================
# 3. RECOGNITION SETTINGS
# =========================================

THRESHOLD = 0.45


# =========================================
# 4. LOAD REGISTERED FACE EMBEDDINGS
# =========================================

registered_embeddings = {}

if not os.path.exists(EMBEDDING_FOLDER):
    print("Face embedding folder not found.")
    exit()

for filename in os.listdir(EMBEDDING_FOLDER):

    if filename.lower().endswith(".npy"):

        student_id = os.path.splitext(filename)[0]

        path = os.path.join(
            EMBEDDING_FOLDER,
            filename
        )

        embedding = np.load(path)

        norm = np.linalg.norm(embedding)

        if norm == 0:
            print(f"Invalid embedding: {student_id}")
            continue

        embedding = embedding / norm

        registered_embeddings[student_id] = embedding


print("\nRegistered students:")

for student_id in registered_embeddings:
    print("-", student_id)


if not registered_embeddings:
    print("No face embeddings found.")
    exit()


# =========================================
# 5. LOAD INSIGHTFACE MODEL
# =========================================

print("\nLoading InsightFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("InsightFace model loaded successfully.")


# =========================================
# 6. TEST DJANGO DATABASE CONNECTION
# =========================================

try:
    student_count = Student.objects.count()

    print("\nDjango database connected successfully.")
    print(f"Total registered students: {student_count}")

except Exception as e:
    print("\nDjango database connection failed:")
    print(e)
    exit()


# =========================================
# 7. START CAMERA
# =========================================

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Cannot open camera.")
    exit()

print("\nCamera started.")
print("Press Q to quit.")


# =========================================
# 8. LIVE FACE RECOGNITION
# =========================================

try:

    while True:

        success, frame = camera.read()

        if not success:
            print("Could not read camera.")
            break

        faces = app.get(frame)

        if len(faces) == 0:

            cv2.putText(
                frame,
                "No face detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        for face in faces:

            # ---------------------------------
            # FACE BOUNDING BOX
            # ---------------------------------

            bbox = face.bbox.astype(int)

            x1, y1, x2, y2 = bbox


            # ---------------------------------
            # GET LIVE FACE EMBEDDING
            # ---------------------------------

            live_embedding = face.embedding

            norm = np.linalg.norm(live_embedding)

            if norm == 0:
                continue

            live_embedding = live_embedding / norm


            # ---------------------------------
            # FIND BEST MATCHING STUDENT
            # ---------------------------------

            best_student = None
            best_similarity = -1

            for student_id, registered_embedding in registered_embeddings.items():

                similarity = float(
                    np.dot(
                        live_embedding,
                        registered_embedding
                    )
                )

                if similarity > best_similarity:

                    best_similarity = similarity
                    best_student = student_id


            # ---------------------------------
            # RECOGNITION DECISION
            # ---------------------------------

            if best_similarity >= THRESHOLD:

                text = f"{best_student} - Recognized"
                box_color = (0, 255, 0)

                print(
                    f"Recognized: {best_student} | "
                    f"Similarity: {best_similarity:.3f}"
                )

            else:

                text = "Unknown Face"
                box_color = (0, 0, 255)

                print(
                    f"Unknown Face | "
                    f"Similarity: {best_similarity:.3f}"
                )


            # ---------------------------------
            # DRAW FACE BOX
            # ---------------------------------

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                box_color,
                2
            )


            # ---------------------------------
            # DISPLAY RECOGNITION RESULT
            # ---------------------------------

            cv2.putText(
                frame,
                text,
                (x1, max(30, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                box_color,
                2
            )


            # ---------------------------------
            # DISPLAY SIMILARITY
            # ---------------------------------

            cv2.putText(
                frame,
                f"Similarity: {best_similarity:.3f}",
                (x1, y2 + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                box_color,
                2
            )


        # =====================================
        # 9. DISPLAY CAMERA
        # =====================================

        cv2.putText(
            frame,
            "Q = Quit",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "SmartAttendAI - InsightFace Recognition",
            frame
        )


        # =====================================
        # 10. QUIT CAMERA
        # =====================================

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


finally:

    camera.release()
    cv2.destroyAllWindows()

    print("\nCamera stopped.")
