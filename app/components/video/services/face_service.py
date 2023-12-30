import typing
import cv2
import os


class FaceService:
    __face_cascade: cv2.CascadeClassifier

    def __init__(self):
        file = 'haarcascade_frontalface_default.xml'
        path_dir = os.path.dirname(cv2.__file__) + '/data/'
        self.__face_cascade = cv2.CascadeClassifier(os.path.join(path_dir, file))

    def detect_faces(self, frame):
        frame = cv2.equalizeHist(frame)

        return self.__face_cascade.detectMultiScale(frame)

    def roi_frame(self, frame, faces: typing.Sequence[cv2.typing.Rect]) -> list:
        roi_list = []
        for (x, y, w, h) in faces:
            roi_list.append(frame[y:y + h, x:x + w])

        roi = []
        for r in roi_list:
            if len(r) > len(roi):
                roi = r

        return roi if len(roi) > 0 else None

    def add_roi_areas(self, frame, faces: typing.Sequence[cv2.typing.Rect]):
        for (x, y, w, h) in faces:
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 240, 120), 2)

        return frame
