import face_recognition
import numpy as np

from ...dto.frame import Frame
from ...exceptions.create_descriptor_exception import CreateDescriptorException
from ...dto.descriptor import Descriptor


class DlDescriptorCreator:

    def create(self, frame: Frame) -> Descriptor:
        """
        :raises CreateDescriptorException
        """

        if frame.faces.frames is None or len(frame.faces.frames) == 0:
            raise CreateDescriptorException()

        encodings = face_recognition.face_encodings(face_image=frame.color, known_face_locations=frame.faces.coordinates)
        encodings = encodings if len(encodings) > 0 else []

        return Descriptor(features=np.array(encodings))
