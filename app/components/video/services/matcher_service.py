from sklearn.metrics.pairwise import euclidean_distances
from ...user.dto.descriptor import Descriptor


class MatcherService:

    def match(self, descriptor: Descriptor, request: Descriptor) -> bool:
        lbh = self.match_lbph(descriptor, request)

        return lbh

    def match_lbph(self, descriptor: Descriptor, request: Descriptor) -> bool:
        min_distance = None

        for lbph in descriptor.lbph:
            distance = min(euclidean_distances([lbph], request.lbph)[0])
            if min_distance is None:
                min_distance = distance

            min_distance = distance if min_distance > distance else min_distance

        print(f"lbph distance: {min_distance}")

        return min_distance < 0.70
