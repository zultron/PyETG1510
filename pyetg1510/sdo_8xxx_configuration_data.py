"""
0x8*** 台のMaster ODを定義したモジュール
"""
from pyetg1510.mailbox.sdo_application_interface import SdoEntry, SdoDataBody, SdoMetadata
from dataclasses import dataclass, field
from pyetg1510.mailbox import SDORequest


@dataclass
class LinkStatus:
    no_link: bool
    """no link"""
    link_no_commm: bool
    """Sub device report a physical link without communication for one or more ports"""
    Link_miss: bool
    """Sub device report a missing link on one or more ports where a link is expected"""
    link_add: bool
    """Sub device report a link on one or more ports where no link is expected"""
    port0: bool
    """one of previous bits refers to port 0"""
    port1: bool
    """one of previous bits refers to port 1"""
    port2: bool
    """one of previous bits refers to port 2"""
    port3: bool
    """one of previous bits refers to port 3"""


@dataclass
class LinkPreset:
    port1_expects_connection: bool
    """Port 1 expects connection to an EtherCAT slave"""
    port2_expects_connection: bool
    """Port 2 expects connection to an EtherCAT slave"""
    port3_expects_connection: bool
    """Port 3 expects connection to an EtherCAT slave"""
    port1_expects_physical_link: bool
    """Port 1 expects physical link"""
    port2_expects_physical_link: bool
    """Port 2 expects physical link"""
    port3_expects_physical_link: bool
    """Port 3 expects physical link"""


class ConfigurationData(SdoDataBody):
    """構成データ オブジェクト 0x8nnn は、サブデバイスのコンフィギュレーションデータが格納されます。
    マスターによって一度だけ更新されます。ホットコネクトグループに属するサブデバイスは最後にリストされます。
    """

    NumberOfEntries: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B"))
    """
    名称:
        エントリ数
    
    """
    FixedStationAddress: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=1, value=0, format="H"))
    """
    名称:
       Fixed Station Address    
    Object:
        0x8nnn:01
    説明:
        `ENI 要素 <https://www.ethercat.org/jp/downloads/downloads_D857E986BC634321840CA5DB43A04D55.htm>`_ の 
        ``Slave:Info:PhysAddr`` の値(各サブデバイスの ESI レジスタのアドレス 0x0010-0x0011 に対応)
    """

    Type: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=2, value="", format="s", size=16))
    """
    名称:
        Type
    Object:
        0x8nnn:02
    説明:
        `ESI 要素 <https://www.ethercat.org/jp/downloads/downloads_6A46D45EA33C47ECB2BB2686BBA963EC.htm>`_ の 
        ``Device:DeviceType:Type`` の値( category General の ``OrderIdx`` [#fn1]_ に対応)
        
    .. [#fn1] `ETG.2010 Slave Information Interface <https://www.ethercat.org/jp/downloads/downloads_AC7ED92675B04BAB9ECD35667A80DFFE.htm>`_  のTable.7に記載
    """
    Name: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=3, value="", format="s", size=32))
    """
    名称:
        Name
    Object:
        0x8nnn:03
    説明:
        `ENI 要素 <https://www.ethercat.org/jp/downloads/downloads_D857E986BC634321840CA5DB43A04D55.htm>`_ の  
        ``Slave:Info:Name`` の値(Object 0x1008 に対応).
    """
    DeviceType: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=4, value=0, format="I"))
    """
    名称:
        Device Type
    Object:
        0x8nnn:04
    説明:
        `ENI 要素 <https://www.ethercat.org/jp/downloads/downloads_D857E986BC634321840CA5DB43A04D55.htm>`_ の 
        ``Device:Profile:ProfileNo (low word)`` と ``Device:Profile:AddInfo (high word)`` の値（object 0x1000に対応）。
        同じ要素が ENI 要素の ``Slave:Mailbox:CoE:ChannelInfo:ProfileNo (low word)`` と 
        ``Slave:Mailbox:CoE:ChannelInfo:AddInfo (high word)`` にも展開されている。
    """
    VendorId: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=5, value=0, format="I"))
    """
    名称:
        Vendor ID, Product Code, Revision, Serial Number
    Object:
        0x8nnn:05-08
    説明:
        `ENI 要素 <https://www.ethercat.org/jp/downloads/downloads_D857E986BC634321840CA5DB43A04D55.htm>`_ の
        ``Slave:Info:VendorId``, ``Slave:Info:ProductCode``, ``Slave:Info:RevisionNo``,
        ``Slave:Info:SerialNo`` の値。 (オブジェクト 0x1018:01-04 に対応).
    """
    ProductCode: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=6, value=0, format="I"))
    RevisionNumber: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=7, value=0, format="I"))
    SerialNumber: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=8, value=0, format="I"))
    MailboxOutSize: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=33, value=0, format="H"))
    """Values of ENI elements Slave:Mailbox:Send:Length and Slave:Mailbox:Receive:Length of slave n
    (correspond to ESC registers 0x0802-0x0803 and 0x080A-0x080B)."""
    MailboxInSize: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=34, value=0, format="H"))
    LinkStatus: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=35, value=0, format="B"))
    """Link status of sub terminal which are also able to get link_preset property"""
    LinkPreset: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=36, value=0, format="B"))
    """Reports the expected physical link on ports 1, 2 and 3 of sub terminal which are also able to get link_preset property"""
    Flags: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=37, value=0, format="B"))
    """Provides additional topology information about redundancy and hot connect"""
    PortPhysics: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=38, value=0, format="H"))
    """Corresponds to ESI element Device:Physics and to ENI element sub:Info:Physics."""
    MailboxProtocolsSupported: SdoEntry = field(
        default_factory=lambda: SdoEntry[int](sub_index=39, value=0, format="H")
    )
    DiagHistoryObjectSupported: SdoEntry = field(
        default_factory=lambda: SdoEntry[bool](sub_index=40, value=False, format="?")
    )

    @property
    def link_status(self) -> LinkStatus:
        args = [bool(self.LinkStatus.value & 1 << i) for i in range(0, 8)]
        return LinkStatus(*args)

    @property
    def link_preset(self) -> LinkPreset:
        args = [bool(self.LinkPreset.value & 1 << i) for i in range(0, 3)]
        args.extend([bool(self.LinkPreset.value & 16 << i) for i in range(0, 3)])
        return LinkPreset(*args)

    @property
    def redundancy_adapter_port(self) -> int:
        """Specified port is connected to secondary master adapter for redundancy purposes.
        zero is not used.
        """
        return self.Flags.value & 0x3

    @property
    def hot_connect_head_terminal(self) -> bool:
        """This terminal is head terminal of hot connect group"""
        return bool(self.Flags.value & 0x4)

    @property
    def hot_connect(self) -> bool:
        """This terminal belong to hot connect group"""
        return bool(self.Flags.value & 0x8)

    @property
    def aoe_supported(self) -> bool:
        return bool(self.MailboxProtocolsSupported.value & 1)

    @property
    def eoe_supported(self) -> bool:
        return bool(self.MailboxProtocolsSupported.value & 2)

    @property
    def coe_supported(self) -> bool:
        return bool(self.MailboxProtocolsSupported.value & 4)

    @property
    def foe_supported(self) -> bool:
        return bool(self.MailboxProtocolsSupported.value & 8)

    @property
    def soe_supported(self) -> bool:
        return bool(self.MailboxProtocolsSupported.value & 16)

    @property
    def voe_supported(self) -> bool:
        return bool(self.MailboxProtocolsSupported.value & 32)


ConfigurationDataFormat = SdoMetadata(
    index=0x8000,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=16,
    request_container=SDORequest,
    response_container=ConfigurationData,
)
