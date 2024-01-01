import cv2

from ...dto.faces import Faces


class FaceDetector:

    def mark_faces(self, video_frame: cv2.typing.MatLike, faces: Faces):
        for (x, y, w, h) in faces.coordinates:
            video_frame = cv2.rectangle(video_frame, (x, y), (x + w, y + h), (100, 240, 120), 2)

        return video_frame
