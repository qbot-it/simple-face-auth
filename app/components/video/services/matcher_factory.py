from .matcher.dl_matcher import DlMatcher
from .matcher.lbph_matcher import LbphMatcher
from ..exceptions.matcher_not_found_exception import MatcherNotFoundException
from ...state.enums.method import Method


class MatcherFactory:

    @staticmethod
    def get_instance(method: Method):
        """
        :raises MatcherNotFoundException
        """
        match method:
            case Method.LBPH:
                return LbphMatcher()
            case Method.DL:
                return DlMatcher()

        raise MatcherNotFoundException()
