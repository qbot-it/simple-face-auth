import cv2
import numpy as np

from ...dto.frame import Frame
from ...exceptions.create_descriptor_exception import CreateDescriptorException
from ...dto.descriptor import Descriptor


class LbphDescriptorCreator:

    def create(self, frame: Frame) -> Descriptor:
        """
        :raises CreateDescriptorException
        """

        if frame.faces.frames is None or len(frame.faces.frames) == 0:
            raise CreateDescriptorException()

        face_features = []

        for face_frame in frame.faces.frames:
            model = cv2.face.LBPHFaceRecognizer().create()
            model.train([face_frame], np.array([1]))
            histograms = model.getHistograms()
            histogram = histograms[0][0]
            if len(histogram) > 0:
                face_features.append(histogram)

        return Descriptor(features=np.array(face_features))
