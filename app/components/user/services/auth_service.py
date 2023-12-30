from ..dto.descriptor import Descriptor
from ...user.models.user import User
from ...video.services.matcher_service import MatcherService


class AuthService:

    __descriptor_matcher_service: MatcherService

    def __init__(self):
        self.__descriptor_matcher_service = MatcherService()

    def passes(self, user: User, descriptor_to_match: Descriptor) -> bool:
        descriptor = Descriptor.from_json(user.descriptor)

        return self.__descriptor_matcher_service.match(descriptor, descriptor_to_match)

