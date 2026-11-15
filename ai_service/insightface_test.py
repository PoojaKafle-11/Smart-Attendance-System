import cv2
from insightface.app import FaceAnalysis

print("Loading InsightFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("InsightFace model loaded successfully!")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open camera.")
    exit()

print("Camera started.")
print("Press Q to quit.")

while True:

    success, frame = camera.read()

    if not success:
        print("Could not read camera.")
        break

    faces = app.get(frame)

    for face in faces:

        bbox = face.bbox.astype(int)

        x1, y1, x2, y2 = bbox

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        # Face embedding
        embedding = face.embedding

        cv2.putText(
            frame,
            "Face Detected",
            (x1, max(30, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        print(
            "Face detected | Embedding size:",
            embedding.shape
        )

    cv2.imshow(
        "SmartAttendAI - InsightFace Test",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("Camera stopped.")