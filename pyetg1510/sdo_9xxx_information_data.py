"""
0x9*** 台のMaster ODを定義したモジュール
"""
from dataclasses import field
from pyetg1510.mailbox.sdo_application_interface import SdoEntry, SdoMetadata, SdoDataBody
from pyetg1510.mailbox import SDORequest


class InformationData(SdoDataBody):
    NumberOfEntries: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B"))
    StationAddress: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H"))
    VendorId: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="I"))
    ProductCode: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="I"))
    RevisionNumber: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="I"))
    SerialNumber: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="I"))
    DLStatusRegister: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="I"))


InformationDataFormat = SdoMetadata(
    index=0x9000,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=16,
    request_container=SDORequest,
    response_container=InformationData,
)
