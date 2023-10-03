"""
0x1*** 台のMaster ODを定義したモジュール
"""
from pyetg1510.mailbox.sdo_application_interface import SdoEntry, SdoDataBody, SdoMetadata
from dataclasses import field
from pyetg1510.mailbox import SDORequest


class DeviceTypeData(SdoDataBody):
    """Contains the Device Type of EtherCAT Master device."""

    DeviceType: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="I"))


class DeviceNameData(SdoDataBody):
    """Contains the Manufacturer Device Name of EtherCAT Master device."""

    DeviceName: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=0, value="", format="s"))


class HardwareVersionData(SdoDataBody):
    """Contains the Manufacturer Hardware Version of EtherCAT Master device."""

    HardwareVersion: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=0, value="", format="s"))


class SoftwareVersionData(SdoDataBody):
    """Contains the Manufacturer Software Version of EtherCAT Master device."""

    SoftwareVersion: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=0, value="", format="s"))


class IndentityObjectData(SdoDataBody):
    """Contains the identification parameter of EtherCAT Master device."""

    NumberOfEntries: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H"))
    """Number of entries of 0x1xxx entry."""
    VendorID: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=1, value=0, format="I"))
    """EtherCAT Vendor ID of master manufacturer."""
    ProductCode: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=2, value=0, format="I"))
    """Code uniquely identifying the specific EtherCAT Master device."""
    RevisionNumber: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=3, value=0, format="I"))
    """Revision of EtherCAT Master device."""
    SerialNumber: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=4, value=0, format="I"))
    """Optional serial number of EtherCAT Master Device (set to 0 if not used)."""


DeviceTypeFormat = SdoMetadata(
    index=0x1000,
    sub_index=0x0000,
    support_complete_access=False,
    max_sub_index=0,
    request_container=SDORequest,
    response_container=DeviceTypeData,
)

DeviceNameFormat = SdoMetadata(
    index=0x1008,
    sub_index=0x0000,
    support_complete_access=False,
    max_sub_index=0,
    request_container=SDORequest,
    response_container=DeviceNameData,
)

HardwareVersionFormat = SdoMetadata(
    index=0x1009,
    sub_index=0x0000,
    support_complete_access=False,
    max_sub_index=0,
    request_container=SDORequest,
    response_container=HardwareVersionData,
)


SoftwareVersionFormat = SdoMetadata(
    index=0x100A,
    sub_index=0x0000,
    support_complete_access=False,
    max_sub_index=0,
    request_container=SDORequest,
    response_container=SoftwareVersionData,
)

IndentityObjectFormat = SdoMetadata(
    index=0x1018,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=0,
    request_container=SDORequest,
    response_container=IndentityObjectData,
)
