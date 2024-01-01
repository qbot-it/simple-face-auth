from ...state.enums.method import Method
from ...user.dto.descriptor import Descriptor
from ...video.dto.frame import Frame
from ...video.services.descriptor_creator_factory import DescriptorCreatorFactory


class DescriptorService:

    def create(self, frame: Frame) -> Descriptor:
        """
        :raises CreateDescriptorException
        """
        lbph_descriptor_creator = DescriptorCreatorFactory.get_instance(Method.LBPH)
        dl_descriptor_creator = DescriptorCreatorFactory.get_instance(Method.DL)

        lbph_descriptor = lbph_descriptor_creator.create(frame)
        dl_descriptor = dl_descriptor_creator.create(frame)

        return Descriptor(lbph=lbph_descriptor.features, dl=dl_descriptor.features)
