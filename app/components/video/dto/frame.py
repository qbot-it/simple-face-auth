import typing
import cv2


class Frame:
    raw: cv2.typing.MatLike
    gray: cv2.typing.MatLike
    color: cv2.typing.MatLike
    faces: typing.Sequence[cv2.typing.Rect]
    roi: list
