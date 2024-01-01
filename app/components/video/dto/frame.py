import cv2

from .faces import Faces


class Frame:
    raw: cv2.typing.MatLike
    color: cv2.typing.MatLike
    faces: Faces
