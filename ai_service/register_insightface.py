import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACE_FOLDER = os.path.join(
    BASE_DIR,
    "ai_service",
    "registered_faces"
)

EMBEDDING_FOLDER = os.path.join(
    BASE_DIR,
    "ai_service",
    "face_embeddings"
)

os.makedirs(EMBEDDING_FOLDER, exist_ok=True)

# -----------------------------
# Load InsightFace
# -----------------------------
print("Loading InsightFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("InsightFace model loaded successfully.")

# -----------------------------
# Process registered images
# -----------------------------
for filename in os.listdir(FACE_FOLDER):

    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    image_path = os.path.join(FACE_FOLDER, filename)

    print(f"\nProcessing: {filename}")

    image = cv2.imread(image_path)

    if image is None:
        print("Could not read image.")
        continue

    faces = app.get(image)

    if len(faces) == 0:
        print("No face detected.")
        continue

    if len(faces) > 1:
        print("More than one face detected. Use an image containing only one person.")
        continue

    face = faces[0]

    # ArcFace 512-dimensional embedding
    embedding = face.embedding

    # Normalize embedding
    embedding = embedding / np.linalg.norm(embedding)

    # Student ID from filename
    student_id = os.path.splitext(filename)[0]

    # Save embedding
    output_path = os.path.join(
        EMBEDDING_FOLDER,
        student_id + ".npy"
    )

    np.save(output_path, embedding)

    print("Student:", student_id)
    print("Embedding size:", embedding.shape)
    print("Saved:", output_path)

print("\nRegistration completed.")