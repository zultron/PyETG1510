"""
0xa*** 台のMaster ODを定義したモジュール
"""
from dataclasses import field, dataclass
from pyetg1510.mailbox.sdo_application_interface import SdoEntry, SdoMetadata, SdoDataBody
from typing import Union, List, Optional
from enum import Enum
from pyetg1510.mailbox import SDORequest


@dataclass
class ALStatusCodeDef:
    """Alarm definition member"""
    code: int
    """Alarm code"""
    occurrence_timing: str
    """Watch timing"""
    transition_state: str
    """Transition of state machine"""
    reference: str
    """Documentation for solution"""

class ALStausCode(Enum):
    """Definition of alarm status code"""
    NoError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0000, occurrence_timing="Any", transition_state="Current", reference="ETG.1000.6"
    )
    UnspecifiedError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0001, occurrence_timing="Any", transition_state="Any +E", reference="ETG.1000.6"
    )
    NoMemory: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0002, occurrence_timing="Any", transition_state="Any +E", reference="ETG.1000.6"
    )
    InvalidRevision: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0004, occurrence_timing="PS", transition_state="P +E", reference="Additionalcode"
    )
    InvalidDeviceSetup: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0003, occurrence_timing="PS", transition_state="P +E", reference="Additionalcode"
    )
    Sii_EEPROMInformationDoesNotMatchFirmware: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0006, occurrence_timing="IP", transition_state="I +E", reference="Additionalcode"
    )
    FirmwareUpdateNotSuccessful_OldFirmwareStillRunning: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0007, occurrence_timing="Boot", transition_state="I +E", reference="Additionalcode"
    )
    LicenseError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x000E, occurrence_timing="Any", transition_state="I +E", reference="Additionalcode"
    )
    InvalidRequestedStateChange: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0011, occurrence_timing="Any", transition_state="Current +E(not O +E)", reference="ETG.1000.6"
    )
    UnknownRequestedState: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0012, occurrence_timing="Any", transition_state="Current +E(not O +E)", reference="ETG.1000.6"
    )
    BootstrapNotSupported: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0013, occurrence_timing="IB", transition_state="I +E", reference="ETG.1000.6"
    )
    NoValidFirmware: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0014, occurrence_timing="IP", transition_state="I +E", reference="ETG.1000.6"
    )
    InvalidMailboxConfigurationBOOT: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0015, occurrence_timing="IB", transition_state="I +E", reference="ETG.1000.6"
    )
    InvalidMailboxConfigurationPREOP: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0016, occurrence_timing="IP", transition_state="I +E", reference="ETG.1000.6"
    )
    InvalidSyncManagerConfiguration: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0017, occurrence_timing="PS, SO", transition_state="Current +E(not O +E)", reference="ETG.1000.6"
    )
    NoValidInputsAvailable: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0018, occurrence_timing="O, SO", transition_state="S +E", reference="ETG.1000.6"
    )
    NoValidOutputs: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0019, occurrence_timing="O, SO", transition_state="S +E", reference="ETG.1000.6"
    )
    SynchronizationError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x001A, occurrence_timing="O, SO", transition_state="S +E", reference="ETG.1000.6"
    )
    SyncManagerWatchdog: ALStatusCodeDef = ALStatusCodeDef(
        code=0x001B, occurrence_timing="O, S", transition_state="S +E", reference="ETG.1000.6"
    )
    InvalidSyncManagerTypes: ALStatusCodeDef = ALStatusCodeDef(
        code=0x001C, occurrence_timing="O, S, PS", transition_state="S +E", reference="ETG.1000.6"
    )
    InvalidOutputConfiguration: ALStatusCodeDef = ALStatusCodeDef(
        code=0x001D, occurrence_timing="O, S, PS", transition_state="S +E", reference="ETG.1000.6"
    )
    InvalidInputConfiguration: ALStatusCodeDef = ALStatusCodeDef(
        code=0x001E, occurrence_timing="O, S, PS", transition_state="S +E", reference="ETG.1000.6"
    )
    InvalidWatchDogConfiguration: ALStatusCodeDef = ALStatusCodeDef(
        code=0x001F, occurrence_timing="O, S, PS", transition_state="P +E", reference="ETG.1000.6"
    )
    SlaveNeedsColdstart: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0020, occurrence_timing="Any", transition_state="Current +E(not O +E)", reference="ETG.1000.6"
    )
    SlaveNeedsInit: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0021, occurrence_timing="B, P, S, O", transition_state="Current +E(not O +E)", reference="ETG.1000.6"
    )
    SlaveNeedsPREOP: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0022, occurrence_timing="S, O", transition_state="Current +E(not O +E)", reference="ETG.1000.6"
    )
    SlaveNeedsSAFEOP: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0023, occurrence_timing="O", transition_state="Current +E(not O +E)", reference="ETG.1000.6"
    )
    InvalidInputMapping: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0024, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    InvalidOutputMapping: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0025, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    InconsistentSettings: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0026, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    FreeRunNotSupported: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0027, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    SynchronizationNotSupported: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0028, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    FreeRunNeeds3BufferMode: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0029, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    BackgroundWatchdog: ALStatusCodeDef = ALStatusCodeDef(
        code=0x002A, occurrence_timing="S, O", transition_state="P +E", reference="ETG.1000.6"
    )
    NoValidInputsAndOutputs: ALStatusCodeDef = ALStatusCodeDef(
        code=0x002B, occurrence_timing="O, SO", transition_state="S +E", reference="ETG.1000.6"
    )
    FatalSyncError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x002C, occurrence_timing="O", transition_state="S +E", reference="ETG.1000.6"
    )
    NoSyncError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x002D, occurrence_timing="SO", transition_state="S +E", reference="ETG.1000.6"
    )
    CycleTimeTooSmall: ALStatusCodeDef = ALStatusCodeDef(
        code=0x002E, occurrence_timing="SO", transition_state="S +E", reference="AdditionalCode"
    )
    InvalidDcSyncConfiguration: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0030, occurrence_timing="O, SO, PS", transition_state="P +E,S +E", reference="ETG.1000.6"
    )
    InvalidDcLatchConfiguration: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0031, occurrence_timing="O, SO, PS", transition_state="P +E,S +E", reference="ETG.1000.6"
    )
    PllError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0032, occurrence_timing="S, O", transition_state="S +E", reference="ETG.1000.6"
    )
    DcSyncIoError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0033, occurrence_timing="O, SO", transition_state="S +E", reference="ETG.1000.6"
    )
    DcSyncTimeoutError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0034, occurrence_timing="O, SO", transition_state="S +E", reference="ETG.1000.6"
    )
    DcInvalidSyncCycleTime: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0035, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    DcSync0CycleTime: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0036, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    DcSync1CycleTime: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0037, occurrence_timing="PS", transition_state="P +E", reference="ETG.1000.6"
    )
    Mbx_Aoe: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0041, occurrence_timing="B, P, S,O", transition_state="Current +ES +E", reference="ETG.1000.6"
    )
    Mbx_Eoe: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0042, occurrence_timing="B, P, S,O", transition_state="Current +ES +E", reference="ETG.1000.6"
    )
    Mbx_Coe: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0043, occurrence_timing="B, P, S,O", transition_state="Current +ES +E", reference="ETG.1000.6"
    )
    Mbx_Foe: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0044, occurrence_timing="B, P, S,O", transition_state="Current +ES +E", reference="ETG.1000.6"
    )
    Mbx_Soe: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0045, occurrence_timing="B, P, S,O", transition_state="Current +ES +E", reference="ETG.1000.6"
    )
    Mbx_Voe: ALStatusCodeDef = ALStatusCodeDef(
        code=0x004F, occurrence_timing="B, P, S,O", transition_state="Current +ES +E", reference="ETG.1000.6"
    )
    EepromNoAccess: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0050, occurrence_timing="Any", transition_state="Any +E(not O +E)", reference="ETG.1000.6"
    )
    EepromError: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0051, occurrence_timing="Any", transition_state="Any +E(not O +E)", reference="ETG.1000.6"
    )
    ExternalHardwareNotReady: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0052, occurrence_timing="Any", transition_state="Any +E(not O +E)", reference="Additionalcode"
    )
    SlaveRestartedLocally: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0060, occurrence_timing="Any", transition_state="I", reference="ETG.1000.6"
    )
    DeviceIdentificationValueUpdated: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0061, occurrence_timing="P", transition_state="P +E", reference="ETG.1000.6"
    )
    DetectedModuleIdentListDoesNotMatch: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0070, occurrence_timing="PS", transition_state="P +E", reference="Additionalcode"
    )
    SupplyVoltageTooLow: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0080, occurrence_timing="Any", transition_state="Any +E(not O +E)", reference="Additionalcode"
    )
    SupplyVoltageTooHigh: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0081, occurrence_timing="Any", transition_state="Any +E(not O +E)", reference="Additionalcode"
    )
    TemperatureTooLow: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0082, occurrence_timing="Any", transition_state="Any +E(not O +E)", reference="Additionalcode"
    )
    TemperatrueTooHigh: ALStatusCodeDef = ALStatusCodeDef(
        code=0x0083, occurrence_timing="Any", transition_state="Any +E(not O +E)", reference="Additionalcode"
    )
    ApplicationControllerAvailable: ALStatusCodeDef = ALStatusCodeDef(
        code=0x00F0, occurrence_timing="I", transition_state="I +E", reference="Additionalcode"
    )

    @classmethod
    def get_al(cls, code: int):
        for obj in cls:
            if code == obj.value.code:
                return obj
        return None


class ALStatus(Enum):
    INIT = 0x0001
    PREOP = 0x0002
    SAFEOP = 0x0004
    OP = 0x0008
    REJECTED = 0x0010
    ALCODE_UPDATED = 0x0020


class LoopControl(Enum):
    """Value of loop control of port X"""
    Auto: int = 0
    """Port loop opens automatically when a physical link is established, and closes automatically when the physical link is lost"""
    AutoClose: int = 1
    """Port loop closes when the physical link is lost, and opens when the physical link is established after explicit request from master"""
    Open: int = 2
    """Port loop is always open, independently from the physical link state"""
    Close: int = 3
    """Port loop is always closed, independently from the physical link state"""

    @classmethod
    def find(cls, value: int):
        for e in LoopControl:
            if e.value == value:
                return e
        raise ValueError(f"{value} is wrong value.")


@dataclass
class PortStatus:
    """Structure of link connection

    use_to_communication=False, link_up=True:
       Used for redundancy

    use_to_communication=True, link_up=True:
       Used for communication with other sub device

    loop_control:
       If not set to Auto, port would not be connected with next port (loop control)
    """
    use_to_communication: bool
    link_up: bool
    loop_control: LoopControl


class DiagnosisData(SdoDataBody):
    """0xAxxx: Diagnosis data of ETG.1510"""
    NumberOfEntries: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B"))
    ALStatus: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=1, value=0, format="H"))
    ALControl: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=2, value=0, format="H"))
    ALStatusCode: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=3, value=0, format="H"))
    LinkConnStatus: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=4, value=0, format="B"))
    LinkControl: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=5, value=0, format="B"))
    FixedAddressConnPort: SdoEntry = field(
        default_factory=lambda: SdoEntry[list](sub_index=6, value=[0, 0, 0, 0], size=8, format="H")
    )
    FrameErrorCounterPort: SdoEntry = field(
        default_factory=lambda: SdoEntry[list](sub_index=10, value=[0, 0, 0, 0], size=16, format="I")
    )
    CyclicWCErrorCounter: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=14, value=0, format="I"))
    SlaveNotPresentCounter: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=15, value=0, format="I"))
    AbnormalStateChangeCounter: SdoEntry = field(
        default_factory=lambda: SdoEntry[int](sub_index=16, value=0, format="I")
    )
    DisableAutomaticLinkControl: SdoEntry = field(
        default_factory=lambda: SdoEntry[bool](sub_index=17, value=False, format="?")
    )
    LastProtocolError: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=18, value=0, format="I"))
    NewDiagMessageAvailable: SdoEntry = field(
        default_factory=lambda: SdoEntry[bool](sub_index=19, value=False, format="?")
    )

    @property
    def port_status(self) -> Union[List[PortStatus], None]:
        """Ports status of sub device"""
        if self.LinkControl.enable and self.LinkConnStatus.enable:
            result = [
                PortStatus(
                    bool(self.LinkConnStatus.value & 1 << p),
                    bool(self.LinkConnStatus.value & 16 << p),
                    LoopControl.find((self.LinkControl.value & 3 << p * 2) >> p * 2),
                )
                for p in range(0, 4)
            ]
            return result
        else:
            return None

    @property
    def al_status_code(self) -> Optional[SdoEntry]:
        """Alarm status of sub device"""
        if self.ALStatusCode.enable:
            return ALStausCode.get_al(self.ALStatusCode.value)
        else:
            return None

    @property
    def al_control(self) -> Optional[SdoEntry]:
        """AL status: Main device control status of state machine"""
        if self.ALStatus.enable:
            return ALStatus(0x0F & self.ALControl.value)
        else:
            return None

    @property
    def al_status(self) -> Optional[SdoEntry]:
        """AL status: Sub device current status of state machine"""
        if self.ALStatus.enable:
            return ALStatus(0x0F & self.ALStatus.value)
        else:
            return None

    @property
    def is_rejected(self) -> Union[bool, None]:
        """AL Control status : Update rejected"""
        if self.ALControl.enable:
            return bool(self.ALControl.value & ALStatus.REJECTED.value)
        else:
            return None

    @property
    def is_updated(self) -> Union[bool, None]:
        """AL Control status : Update successfully"""
        if self.ALControl.enable:
            return bool(self.ALControl.value & ALStatus.ALCODE_UPDATED.value)
        else:
            return None

DiagnosisDataFormat = SdoMetadata(
    index=0xA000,
    sub_index=0x0000,
    support_complete_access=True,
    max_sub_index=32,
    request_container=SDORequest,
    response_container=DiagnosisData,
)
