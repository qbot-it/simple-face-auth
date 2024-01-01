import cv2
from numpy import ndarray

from .face_detector import FaceDetector
from ...dto.faces import Faces


class HaarFaceDetector(FaceDetector):
    __face_cascade: cv2.CascadeClassifier

    def __init__(self):
        self.__face_cascade = cv2.CascadeClassifier('files/haarcascade_frontalface_default.xml')

    def faces(self, raw_video_frame: ndarray) -> Faces:
        video_frame = cv2.equalizeHist(cv2.cvtColor(raw_video_frame, cv2.COLOR_BGR2GRAY))
        coordinates_list = self.__face_cascade.detectMultiScale(video_frame)

        max_face_frame = []
        max_face_frame_coordinates = []
        for coordinates in coordinates_list:
            x, y, w, h = coordinates
            face_frame = video_frame[y:y + h, x:x + w]
            if len(face_frame) > len(max_face_frame):
                max_face_frame = face_frame
                max_face_frame_coordinates = coordinates

        faces = Faces()
        if len(max_face_frame_coordinates) > 0:
            faces.coordinates = [max_face_frame_coordinates]
            faces.frames = [max_face_frame]

        return faces
