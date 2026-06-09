import pickle
import cv2
import numpy as np

from database import get_connection
from face_engine import app


def load_students():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT student_id,name,roll_no,embedding
    FROM students
    WHERE embedding IS NOT NULL
    """)

    rows = cursor.fetchall()

    conn.close()

    students = []

    for row in rows:

        student_id = row[0]
        name = row[1]
        roll_no = row[2]

        embedding = pickle.loads(row[3])

        students.append({
            "student_id": student_id,
            "name": name,
            "roll_no": roll_no,
            "embedding": embedding
        })

    return students


def cosine_similarity(a, b):

    return np.dot(a, b) / (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )


def recognize_faces(frame):

    students = load_students()

    faces = app.get(frame)

    results = []

    for face in faces:

        current_embedding = face.embedding

        best_score = 0
        best_student = None

        for student in students:

            score = cosine_similarity(
                current_embedding,
                student["embedding"]
            )

            if score > best_score:
                best_score = score
                best_student = student

        if best_score > 0.60:

            results.append({
                "student_id": best_student["student_id"],
                "name": best_student["name"],
                "roll_no": best_student["roll_no"],
                "score": float(best_score)
            })

    return results
def recognize_from_image(image):

    students = load_students()

    faces = app.get(image)

    results = []

    for face in faces:

        current_embedding = face.embedding

        best_score = 0
        best_student = None

        for student in students:

            score = cosine_similarity(
                current_embedding,
                student["embedding"]
            )

            if score > best_score:

                best_score = score
                best_student = student

        if (
            best_student is not None
            and best_score > 0.60
        ):

            results.append({
                "student_id":
                best_student["student_id"],

                "name":
                best_student["name"],

                "roll_no":
                best_student["roll_no"],

                "score":
                float(best_score)
            })

    return results