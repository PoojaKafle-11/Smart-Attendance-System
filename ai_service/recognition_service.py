
import os
import cv2
import numpy as np

from pathlib import Path
from insightface.app import FaceAnalysis


# =========================================
# 1. PROJECT PATHS
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDING_FOLDER = BASE_DIR / "ai_service" / "face_embeddings"

THRESHOLD = 0.45


# =========================================
# 2. LOAD RECOGNITION MODEL
# =========================================

face_app = None
registered_embeddings = None


def load_recognition_system():

    global face_app, registered_embeddings

    if face_app is not None and registered_embeddings is not None:
        return

    print("Loading InsightFace model...")

    face_app = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )

    face_app.prepare(
        ctx_id=0,
        det_size=(640, 640)
    )

    print("InsightFace model loaded.")

    registered_embeddings = {}

    if not EMBEDDING_FOLDER.exists():
        raise FileNotFoundError(
            f"Embedding folder not found: {EMBEDDING_FOLDER}"
        )

    for file in EMBEDDING_FOLDER.glob("*.npy"):

        student_id = file.stem

        embedding = np.load(file)

        norm = np.linalg.norm(embedding)

        if norm == 0:
            continue

        embedding = embedding / norm

        registered_embeddings[student_id] = embedding

    if not registered_embeddings:
        raise ValueError("No registered face embeddings found.")

    print(
        f"Loaded {len(registered_embeddings)} student embeddings."
    )


# =========================================
# 3. RECOGNIZE FACE FROM IMAGE
# =========================================

def recognize_face(image_bytes):

    load_recognition_system()

    # Convert browser image bytes into OpenCV image
    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    frame = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if frame is None:
        raise ValueError("Invalid camera image.")

    faces = face_app.get(frame)
    print("Image shape:", frame.shape)
    print("Faces detected:", len(faces))

    if not faces:
        return {
            "recognized": False,
            "message": "No face detected."
        }

    results = []

    for face in faces:

        live_embedding = face.embedding

        norm = np.linalg.norm(live_embedding)

        if norm == 0:
            continue

        live_embedding = live_embedding / norm

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

        if best_student and best_similarity >= THRESHOLD:
            print("Best matching student:", best_student)
            print("Best similarity:", best_similarity)
            print("Required threshold:", THRESHOLD)

            results.append({
                "recognized": True,
                "student_id": best_student,
                "similarity": best_similarity
            })

        else:

            results.append({
                "recognized": False,
                "message": "Unknown face.",
                "similarity": best_similarity
            })

    if not results:
        return {
            "recognized": False,
            "message": "Could not process detected face."
        }

    # Return the strongest match for now.
    return max(
        results,
        key=lambda result: result.get("similarity", -1)
    )
