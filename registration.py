from fastapi import APIRouter, UploadFile, File
from models import StudentRegister
from database import get_connection

import cv2
import os
import pickle
import numpy as np

from face_engine import get_face_embedding_from_image

router = APIRouter()

STUDENT_FOLDER = "students"
os.makedirs(STUDENT_FOLDER, exist_ok=True)


@router.post("/register-student")
def register_student(student: StudentRegister):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
    INSERT INTO students
    (
        student_id,
        name,
        roll_no,
        class_name,
        section
    )
    VALUES (?,?,?,?,?)
""",
(
    student.student_id,
    student.name,
    student.roll_no,
    student.class_name,
    student.section
))

        conn.commit()

        return {
            "success": True,
            "message": "Student Registered Successfully"
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

    finally:
        conn.close()


@router.post("/upload-face/{student_id}")
async def upload_face(
    student_id: str,
    file: UploadFile = File(...)
):

    image_bytes = await file.read()

    np_array = np.frombuffer(
        image_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        np_array,
        cv2.IMREAD_COLOR
    )

    if image is None:

        return {
            "success": False,
            "message": "Invalid Image"
        }

    image_path = os.path.join(
        STUDENT_FOLDER,
        f"{student_id}.jpg"
    )

    cv2.imwrite(
        image_path,
        image
    )

    embedding = get_face_embedding_from_image(
        image
    )

    if embedding is None:

        return {
            "success": False,
            "message": "No Face Detected"
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE students
    SET photo_path=?,
        embedding=?
    WHERE student_id=?
    """,
    (
        image_path,
        pickle.dumps(embedding),
        student_id
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "photo_saved": image_path
    }

@router.post("/recognize-face")
async def recognize_face(
    file: UploadFile = File(...)
):

    image_bytes = await file.read()

    np_array = np.frombuffer(
        image_bytes,
        np.uint8
    )

    image = cv2.imdecode(
        np_array,
        cv2.IMREAD_COLOR
    )

    if image is None:

        return {
            "success": False,
            "message": "Invalid Image"
        }

    from recognition import recognize_faces

    results = recognize_faces(image)

    if len(results) == 0:

        return {
            "success": False,
            "message": "Unknown Face"
        }

    student = results[0]

    from attendance import mark_attendance

    mark_attendance(student)

    return {
        "success": True,
        "student": student
    }