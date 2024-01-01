from .descriptor.dl_descriptor_creator import DlDescriptorCreator
from .descriptor.lbph_descriptor_creator import LbphDescriptorCreator
from ...state.enums.method import Method
from ..exceptions.descriptor_creator_not_found_exception import DescriptorCreatorNotFoundException


class DescriptorCreatorFactory:

    @staticmethod
    def get_instance(method: Method):
        """
        :raises DescriptorCreatorNotFoundException
        """
        match method:
            case Method.LBPH:
                return LbphDescriptorCreator()
            case Method.DL:
                return DlDescriptorCreator()

        raise DescriptorCreatorNotFoundException()
