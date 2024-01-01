from sklearn.metrics.pairwise import euclidean_distances

from ...dto.descriptor import Descriptor
from ....user.dto.descriptor import Descriptor as UserDescriptor


class LbphMatcher:

    def match(self, descriptor: UserDescriptor, request: Descriptor) -> bool:
        min_distance = None

        for lbph in descriptor.lbph:
            for vector in request.features:
                distance = min(euclidean_distances([lbph], [vector]))
                if min_distance is None:
                    min_distance = distance

                min_distance = distance if min_distance > distance else min_distance

        print(f"lbph distance: {min_distance}")

        return min_distance < 0.70
