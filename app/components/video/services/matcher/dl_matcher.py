import face_recognition

from ...dto.descriptor import Descriptor
from ....user.dto.descriptor import Descriptor as UserDescriptor


class DlMatcher:

    def match(self, descriptor: UserDescriptor, request: Descriptor) -> bool:
        for encoding in request.features:
            results = face_recognition.compare_faces(descriptor.dl, encoding)
            if True in results:
                return True

        return False
