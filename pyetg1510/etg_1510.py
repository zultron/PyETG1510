"""
ETG.1510 data acquisition control module.

Reference the data model through metadata defined in modules starting with ``sdo_*xxx_``.
"""
from dataclasses import dataclass, field, fields
from pyetg1510.mailbox.connection import EtherCATMasterConnection
from pyetg1510.mailbox.sdo_application_interface import (
    SdoDataBody,
    ConcreteSDODataFactory,
    is_primitive,
    SdoMetadataMapper,
    MappingMember,
    SdoDataController,
    ODListFormat,
    SDOInfoDescriptionFormat,
    SDOInfoEntryFormat,
)
from pyetg1510.sdo_1xxx_master_object import (
    DeviceTypeFormat,
    DeviceNameFormat,
    HardwareVersionFormat,
    SoftwareVersionFormat,
    IndentityObjectFormat,
)
from pyetg1510.sdo_8xxx_configuration_data import ConfigurationDataFormat
from pyetg1510.sdo_9xxx_information_data import InformationDataFormat
from pyetg1510.sdo_axxx_master_diagnosis import DiagnosisDataFormat
from pyetg1510.sdo_fxxx_controls import (
    DetectModulesCommandFormat,
    MasterDiagDataFormat,
    DiagInterfaceControlFormat,
    ConfiguredAddressListFormat,
)
from typing import List, Tuple
from pyetg1510.helper import SysLog

logger = SysLog.logger


class MasterDiagnosisMetadataMapper(SdoMetadataMapper):
    """Class associating defined SDO metadata with its index range

    Associates :obj:`metadata <pyetg1510.mailbox.sdo_data_factory.SdoMetadata>`
    with index range.

    You can select any member using the base class
    :mod:`pyetg1510.mailbox.sdo_data_factory.SdoMetadataMapper.find` method.
    """

    device_type = MappingMember(index_range=(0x1000, 0x1000), metadata=DeviceTypeFormat)
    device_name = MappingMember(index_range=(0x1008, 0x1008), metadata=DeviceNameFormat)
    hardware_vaersion = MappingMember(index_range=(0x1009, 0x1009), metadata=HardwareVersionFormat)
    software_vaersion = MappingMember(index_range=(0x100A, 0x100A), metadata=SoftwareVersionFormat)
    indentity_object = MappingMember(index_range=(0x1018, 0x1018), metadata=IndentityObjectFormat)
    master_configuration = MappingMember(index_range=(0x8000, 0x8FFF), metadata=ConfigurationDataFormat)
    master_information = MappingMember(index_range=(0x9000, 0x9FFF), metadata=InformationDataFormat)
    diagnosis_data = MappingMember(index_range=(0xA000, 0xAFFF), metadata=DiagnosisDataFormat)
    detect_modules_command = MappingMember(index_range=(0xF002, 0xF002), metadata=DetectModulesCommandFormat)
    configured_address_list = MappingMember(index_range=(0xF020, 0xF020), metadata=ConfiguredAddressListFormat)
    master_diag_data = MappingMember(index_range=(0xF120, 0xF120), metadata=MasterDiagDataFormat)
    diag_interface_control = MappingMember(index_range=(0xF200, 0xF200), metadata=DiagInterfaceControlFormat)


@dataclass
class MasterODSpecification:
    """Manage SDO information supported by the EtherCAT main device.

    Manage SDO information collected by the SDO Information service [#f1].

    .. [#f1] `ETG.1000.6 <https://www.ethercat.org/jp/downloads/downloads_A02E436C7A97479F9261FDFA8A6D71E5.htm>`_ Section 5.6.3

    Args:
        connection(EtherCATMasterConnection): Communication connector object
    """

    connection: EtherCATMasterConnection
    sdo_data_entity: ConcreteSDODataFactory = field(
        default_factory=ConcreteSDODataFactory, init=False
    )

    def __post_init__(self):
        self.data_handler = SdoDataController(session=self.connection, get_info=True)
        self.current_index = 0
        self.current_subindex = 0

    async def get_object_dictionary(self):
        """Inquire about the OD of the main device.

        Uses SDO Information service and register its specifications to
        sdo_data_entry.

        Perform the following steps:

        1. Collect OD List and use :obj:`Metadata mapper
           <pyetg1510.etg_1510.MasterDiagnosisMetadataMapper>` Get the
           corresponding :obj:`metadata
           <pyetg1510.mailbox.sdo_data_factory.SdoMetadata>`
        2. Create an entity based on the template using
           :mod:`ConcreteSDODataFactory` and register it in sdo_data_entry.
        3. Request the description of each OD and update the created entity
           according to the response.
        4. The data queried by sdo_data_entry is created.
        """
        logger.info("Fetch OD List")
        await self.data_handler.fetch(
            sdo_metadata=ODListFormat, sdo_data=ODListFormat.response_container()
        )

        for self.current_index in self.data_handler.sdo_data.ObjectIndex.value:
            logger.info(
                f"==== Index {self.current_index},"
                f" format :{ODListFormat.response_container.__name__}"
            )
            _selected: MappingMember = MasterDiagnosisMetadataMapper.find(
                self.current_index
            )
            if _selected is not None:
                # Create instances by sdo factory.
                self.sdo_data_entity.create(
                    index=self.current_index,
                    template=_selected.metadata.response_container
                )
            else:
                logger.warning(
                    f"Index : {self.current_index}"
                    " is not defined for any specification."
                )
                continue
            SDOInfoDescriptionFormat.index = self.current_index
            logger.info("Fetch Object Description")
            await self.data_handler.fetch(
                sdo_metadata=SDOInfoDescriptionFormat,
                sdo_data=SDOInfoDescriptionFormat.response_container()
            )
            # apply max subindex to configuration model
            if hasattr(self.data_handler.sdo_data, "MaxSubindex"):
                sdo_data = self.data_handler.sdo_data
                _selected.metadata.max_sub_index = sdo_data.MaxSubindex.value
            else:
                _selected.metadata.max_sub_index = 0
            logger.info(f"Max sub index: {_selected.metadata.max_sub_index}")
            for field in fields(self.sdo_data_entity.entries[self.current_index]):
                entry = getattr(self.sdo_data_entity.entries[self.current_index], field.name)
                self.current_subindex = entry.sub_index
                logger.info(f"   ---- Subindex {self.current_subindex}")
                SDOInfoEntryFormat.index = self.current_index
                SDOInfoEntryFormat.sub_index = self.current_subindex
                logger.info("Fetch Entry Description")
                await self.data_handler.fetch(
                    sdo_metadata=SDOInfoEntryFormat, sdo_data=SDOInfoEntryFormat.response_container()
                )
                if "AbortCode" not in self.data_handler.sdo_data.__dict__:
                    if entry is not None:
                        entry.name = self.data_handler.sdo_data.Data.value
                        if is_primitive(entry.value):
                            entry.size = int(self.data_handler.sdo_data.BitLength.value / 8)
                        entry.enable = True
                        logger.info(
                            f"Index: {self.current_index}. Subindex:{self.current_subindex} is Enabled. Size:{entry.size}"
                        )
                        logger.info(f"     {entry}")
                    else:
                        logger.error(f"{self.current_index}:{self.current_subindex} is not found on definition.")

        logger.info("============ Information data fetch complete ==============")


@dataclass
class ETG1510Profile:
    """ETG.1510 Data collection asynchronous iterator.

    Iterator class that sequentially collects and returns SDOs according to the
    OD list set in master_od.

    Example of use:
        .. code-block:: python

            async def get_sdo_data():
                # create iterator object
                ittr = ETG1510Profile(master_od=<<OD data model created with MasterConfiguration class>>)
                async for sdo in ittr:
                    # sdo will be possible to get each SDO as SdoDataBody type or Dictionary type.
                    pass

    Args:
        master_od(MasterODSpecification): :meth:`<pyetg1510.etg_1510.MasterODSpecification.get_object_dictionary>`
            MasterODSpecification object after completing collecting OD by running
        watch_index_list(List[int]): SDO index list to watch. If undefined, all ODs are targeted.

    Return:
        Tuple[int, SdoDataBody]: SDO index, retrieved SDO data container
    """

    master_od: MasterODSpecification
    """Collected main device object dictionary"""
    watch_index_list: List[int] = None
    """
    When collecting with an iterator, if you want to specify the index list to be
    collected, set that list. If not specified, return all
    """

    def __post_init__(self):
        self.data_handler = SdoDataController(session=self.master_od.connection, get_info=False)
        self.watch_address = 0
        self.sdo_database = self.master_od.sdo_data_entity.entries

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.watch_index_list is None:
            sdo_index_list = list(self.master_od.sdo_data_entity.entries.keys())
        else:
            sdo_index_list = self.watch_index_list
        if len(sdo_index_list) <= self.watch_address:
            self.watch_address = 0
            raise StopAsyncIteration
        # ToDo: sdo_index_listの要素に self.master_od.sdo_data_entity.entries.keys() が含まれなければ異常終了する
        sdo_metadata = MasterDiagnosisMetadataMapper.find(sdo_index_list[self.watch_address]).metadata
        sdo_metadata.index = sdo_index_list[self.watch_address]
        logger.info(f"==== Fetch and update data index:{sdo_index_list[self.watch_address]}")
        await self.data_handler.fetch(
            sdo_metadata=sdo_metadata, sdo_data=self.sdo_database[sdo_index_list[self.watch_address]]
        )
        report = (sdo_index_list[self.watch_address], self.data_handler.sdo_data)
        self.watch_address += 1
        return report

    async def get_sdo(self, index: int) -> SdoDataBody:
        """Get the SDO of the specified index.

        Args:
            index(int): SDO index
        Return:
            SdoDataBody: Obtained SDO data container
        """
        sdo_metadata = MasterDiagnosisMetadataMapper.find(index).metadata
        sdo_metadata.index = index
        await self.data_handler.fetch(sdo_metadata=sdo_metadata, sdo_data=self.sdo_database[index])

        return self.data_handler.sdo_data
