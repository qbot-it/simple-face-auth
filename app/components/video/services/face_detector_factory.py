from .detector.haar_face_detector import HaarFaceDetector
from ..exceptions.face_detector_not_found_exception import FaceDetectorNotFoundException
from ...state.enums.method import Method


class FaceDetectorFactory:

    @staticmethod
    def get_instance(method: Method):
        """
        :raises FaceDetectorNotFoundException
        """
        match method:
            case Method.LBPH:
                return HaarFaceDetector()
            case Method.DL:
                return HaarFaceDetector()

        raise FaceDetectorNotFoundException()
