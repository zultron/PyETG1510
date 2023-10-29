"""
0xf*** 台のMaster ODを定義したモジュール
"""
from pyetg1510.mailbox.sdo_application_interface import SdoEntry, SdoMetadata, SdoDataBody
from dataclasses import field
from pyetg1510.mailbox import SDORequest
from typing import Union


class DetectModulesCommand(SdoDataBody):
    NumberofEntries: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B"))
    ScanCommandRequest: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=1, value="", format="2s"))
    ScanCommandStatus: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=2, value=0, format="B"))
    ScanCommandResponse: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=3, value="", format="6s"))


class ConfiguredAddressList(SdoDataBody):
    NumberofSlaves: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B"))
    ConfiguredAddress: SdoEntry = field(default_factory=lambda: SdoEntry[list](sub_index=1, value=[0] * 125, format="H"))

    @property
    def address_list(self) -> Union[list, None]:
        if self.ConfiguredAddress.enable:
            return self.ConfiguredAddress.value[:self.NumberofSlaves.value]
        else:
            return None


class MasterDiagData(SdoDataBody):
    NumberOfEntries: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B"))
    CyclicLostFrames: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=1, value=0, format="I"))
    ACyclicLostFrames: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=2, value=0, format="I"))
    CyclicFramesPerSecond: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=3, value=0, format="I"))
    ACyclicFramesPerSecond: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=4, value=0, format="I"))
    MasterState: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=16, value=0, format="H"))


class DiagInterfaceControl(SdoDataBody):
    NumberOfEntries: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B"))
    ResetDiagInfo: SdoEntry = field(default_factory=lambda: SdoEntry[bool](sub_index=16, value=0, format="?"))


DetectModulesCommandFormat = SdoMetadata(
    index=0xF002,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=3,
    request_container=SDORequest,
    response_container=DetectModulesCommand,
)

ConfiguredAddressListFormat = SdoMetadata(
    index=0xF020,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=0x7F,
    request_container=SDORequest,
    response_container=ConfiguredAddressList,
)


MasterDiagDataFormat = SdoMetadata(
    index=0xF120,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=16,
    request_container=SDORequest,
    response_container=MasterDiagData,
)

DiagInterfaceControlFormat = SdoMetadata(
    index=0xF200,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=16,
    request_container=SDORequest,
    response_container=DiagInterfaceControl,
)
