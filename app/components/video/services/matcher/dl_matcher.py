import face_recognition

from ...dto.descriptor import Descriptor
from ....user.dto.descriptor import Descriptor as UserDescriptor


class DlMatcher:

    def match(self, descriptor: UserDescriptor, request: Descriptor) -> bool:
        not_empty = []

        for dl in descriptor.dl:
            if len(dl) > 0:
                not_empty.append(dl)

        rdl = request.features[0] if len(request.features) > 1 else request.features

        if len(not_empty) > 0 and len(rdl) > 0:
            for vector in not_empty:
                results = face_recognition.compare_faces(vector, rdl)
                if len(results) > 0:
                    return True

        return False
