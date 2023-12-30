import cv2
import numpy as np
from ..dto.frame import Frame
from ..exceptions.create_descriptor_exception import CreateDescriptorException
from ...user.dto.descriptor import Descriptor


class DescriptorService:

    def create(self, frame: Frame) -> Descriptor:
        """
        :raises CreateDescriptorException
        """

        if frame.roi is None or len(frame.roi) == 0:
            raise CreateDescriptorException()

        model = cv2.face.LBPHFaceRecognizer().create()
        model.train([frame.roi], np.array([1]))
        histograms = model.getHistograms()
        histogram = histograms[0]

        return Descriptor(lbph=np.array(histogram))
