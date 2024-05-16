"""Mailbox Gateway communication frame control module

"""
import sys
from ctypes import *
from bitarray import bitarray, util
from dataclasses import dataclass, field
from enum import Enum
from typing import Union
from pyetg1510.helper import SysLog

logger = SysLog.logger


class EtherCATProtocolType(Enum):
    PDU = 0x01
    """Protocol Data Unit"""
    NETWORK_VARIABLES = 0x04
    MAILBOX = 0x05


class SdoService(Enum):
    REQUEST = 0x02
    RESPONSE = 0x03
    INFO = 0x08


class SdoRequestCommand(Enum):
    SDOREQ_DOWNLOAD_SEGMENTED = 0x00
    """Req/Download Segmented Res/Upload Segmented"""
    SDOREQ_DOWNLOAD = 0x01
    """Req/Download Res/Download Segmented Info/Get OD List Req."""
    SDOREQ_UPLOAD = 0x02
    """Req/Upload Res/Upload Info/Get OD List Resp."""
    SDOREQ_UPLOAD_SEGMENTED = 0x03
    """Req/Upload Segmented Res/Download Info/Get Object Description Req."""
    SDOREQ_ABORT_TRANSFER = 0x04
    """Req/Abort Transfer Info./Get Object Description Resp."""


class SdoInfoOpcode(Enum):
    GET_OD_LIST_REQ = 0x01
    GET_OD_LIST_RES = 0x02
    GET_DESCRIPTION_REQ = 0x03
    GET_DESCRIPTION_RES = 0x04
    GET_ENTRY_REQ = 0x05
    GET_ENTRY_RES = 0x06
    SDO_INFO_ERR_REQ = 0x07


class SdoResponseCommand(Enum):
    SDORES_UPLOAD_SEGMENTED = 0x00
    """Req/Download Segmented Res/Upload Segmented"""
    SDORES_DOWNLOAD_SEGMENTED = 0x01
    """Req/Download Res/Download Segmented Info/Get OD List Req."""
    SDORES_UPLOAD = 0x02
    """Req/Upload Res/Upload Info/Get OD List Resp."""
    SDORES_DOWNLOAD = 0x03
    """Req/Upload Segmented Res/Download Info/Get Object Description Req."""


class SdoInfoCommand(Enum):
    SDOINFO_ODLIST_REQ = 0x01
    """Req/Download Res/Download Segmented Info/Get OD List Req."""
    SDOINFO_ODLIST_RES = 0x02
    """Req/Upload Res/Upload Info/Get OD List Resp."""
    SDOINFO_DESCRIPTION_REQ = 0x03
    """Req/Upload Segmented Res/Download Info/Get Object Description Req."""
    SDOINFO_DESCRIPTION_RES = 0x04
    """Req/Abort Transfer Info./Get Object Description Resp."""
    SDOINFO_ENTRY_REQ = 0x05
    """Info/Get Entry Description."""
    SDOINFO_ENTRY_RES = 0x06
    """Info/Get Entry Description Resp."""
    SDOINFO_INFO_ERR_REQ = 0x07
    """Info/SDO Info Error Req."""


class MailBoxFrameOffsetAddress(Enum):
    ETHERCAT_HEADER = 0
    MAILBOX_HEADER = 2
    COE_HEADER = 8
    SDO_HEADER = 10
    SDO_DATA = 14


class EtherCATHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ("Length", c_uint16, 11),  # 'H' -> int
        ("Reserved", c_uint8, 1),  # '?' -> bool
        ("DataType", c_uint8, 4),  # 'B' -> int
    ]


class MailboxHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ("Length", c_uint16, 16),  # 'H' -> int
        ("Address", c_uint16, 16),  # 'H' -> int
        ("Channel", c_uint8, 6),  # 'B' -> int
        ("Prio", c_uint8, 2),  # 'B' -> int
        ("Type", c_uint8, 4),  # 'B' -> int
        ("Cnt", c_uint8, 3),  # 'B' -> int
        ("Reserved", c_uint8, 1),  # '?' -> bool
    ]


class CoEHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ("Number", c_uint16, 9),  # 'H' -> int
        ("Reserved", c_uint8, 3),  # 'B' -> int
        ("Service", c_uint8, 4),  # 'B' -> int
    ]


class SDORequest(Structure):
    _pack_ = 1
    _fields_ = [
        ("Reserved", c_uint8, 4),  # 'H' -> int
        ("CompleteAccess", c_uint8, 1),  # '?' -> bool
        ("CommandSpecifier", c_uint8, 3),  # 'B' -> int
        ("Index", c_uint16, 16),  # 'H' -> int
        ("SubIndex", c_uint8, 8),  # 'B' -> int
        ("Reserved2", c_uint32, 32),  # 'H' -> int
    ]


class SDOResponse(Structure):
    _pack_ = 1
    _fields_ = [
        ("SizeIndicator", c_uint8, 1),  # True : enable following size specification
        ("TransferType", c_uint8, 1),  # True: Expedited / False: Normal
        ("DataSetSize", c_uint8, 2),  # 0: 4byte, 1 : 3byte, 2: 2byte, 3: 1byte
        ("CompleteAccess", c_uint8, 1),  # multi subindex
        ("CommandSpecifier", c_uint8, 3),  # defined as 'SdoResponseCommand' enum type
        ("Index", c_uint16, 16),  # 'H' -> int
        ("SubIndex", c_uint8, 8),  # 'B' -> int
    ]


class SDOInformationHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ("Opcode", c_uint8, 7),  #
        ("Incomplete", c_uint8, 1),  #
        ("Reserved", c_uint8, 8),  #
        ("FragmentsLeft", c_uint16, 16),  #
    ]


class SDOInformationODListRequest(Structure):
    _fields_ = [("ListType", c_uint16, 16)]


class SDOInformationDescriptionRequest(Structure):
    _fields_ = [
        ("Index", c_uint16, 16),
    ]


class SDOInformationEntryRequest(Structure):
    _fields_ = [("Index", c_uint16, 16), ("Subindex", c_uint8, 8), ("ValueInfo", c_uint8, 8)]


@dataclass
class SDOMessage:
    sdo_service: SdoService = field(default_factory=SdoService, init=True)
    station_address: int = field(default=0x0000, init=True)  # Default: Master
    mailbox_type: int = field(default=0x03, init=True)  # Default: CoE
    session_counter: int = field(default=1, init=False)
    index: int = field(default_factory=int, init=False)
    sub_index: int = field(default_factory=int, init=False)
    complete_access: bool = field(default_factory=bool, init=False)
    sdo_command: Union[SdoRequestCommand, SdoResponseCommand] = field(
        default=SdoRequestCommand.SDOREQ_UPLOAD, init=False
    )
    ethercat_header: EtherCATHeader = field(default_factory=EtherCATHeader, init=False)
    mailbox_header: MailboxHeader = field(default_factory=MailboxHeader, init=False)
    coe_header: CoEHeader = field(default_factory=CoEHeader, init=False)

    def __new__(cls, *args, **kwargs):
        dataclass(cls)
        return super().__new__(cls)

    def __post_init__(self):
        if self.sdo_service == SdoService.REQUEST:
            self.sdo_header = SDORequest()
        elif self.sdo_service == SdoService.RESPONSE:
            self.sdo_header = SDOResponse()
        elif self.sdo_service == SdoService.INFO:
            self.sdo_header = SDOInformationHeader()

    def get_bytes(self, source: Structure) -> bitarray:
        """Get bitarray object"""

        # Works for either Python2 or Python3

        _bitarray = bitarray(endian=sys.byteorder)
        _bitarray[:] = 0

        for item in source._fields_:
            a = bitarray(endian=sys.byteorder)
            a[:] = 0
            value = getattr(source, item[0])
            a.frombytes(value.to_bytes(length=1 + int(item[2] / 8), byteorder=sys.byteorder))

            if a.endian() == "big":
                a = a[0 - item[2] :]
                _bitarray = a + _bitarray
            else:
                a = a[0 : item[2]]
                _bitarray = _bitarray + a

        if _bitarray.endian() != "big":
            _bitarray.bytereverse()

        return _bitarray

    def make_coe_header(self, sdo_data_size: int, increase_session: bool = True) -> bitarray:
        # CoE Header message parameter set
        self.coe_header.Number = 0
        self.coe_header.Reserved = 0
        self.coe_header.Service = self.sdo_service.value
        coe_header_bytes = self.get_bytes(self.coe_header)
        body_size = int((sdo_data_size + len(coe_header_bytes)) / 8)
        self.mailbox_header.Length = body_size
        self.mailbox_header.Address = self.station_address
        self.mailbox_header.Channel = 0
        self.mailbox_header.Prio = 0
        self.mailbox_header.Type = self.mailbox_type

        # Mailbox Header message parameter set
        if self.session_counter > 7 or self.session_counter <= 0:
            raise ValueError(f"session_counter must be within 1-7. Set to {self.session_counter}")

        if increase_session:
            if self.session_counter >= 7 or self.session_counter <= 0:
                self.session_counter = 1
            else:
                self.session_counter += 1

        self.mailbox_header.Cnt = self.session_counter
        self.mailbox_header.Reserved = 0
        mailbox_header_bytes = self.get_bytes(self.mailbox_header)

        # EtherCAT Header message parameter set
        total_length = int(len(mailbox_header_bytes) / 8) + body_size

        self.ethercat_header.Length = total_length
        self.ethercat_header.Reserved = 0
        self.ethercat_header.DataType = EtherCATProtocolType.MAILBOX.value
        ecat_header_bytes = self.get_bytes(self.ethercat_header)

        # join whole frames
        _bitarray = bitarray()
        _bitarray.extend(ecat_header_bytes)
        _bitarray.extend(mailbox_header_bytes)
        _bitarray.extend(coe_header_bytes)

        return _bitarray


class SDOResponseMessage(SDOMessage):
    """deserialize received byte message until coe header.
    If you find deserialize logic for sdo message body, you should see map method at the PySdoDataMode.SdoController
    """

    def __post_init__(self):
        super().__post_init__()
        if self.sdo_service not in [SdoService.RESPONSE, SdoService.INFO]:
            raise ValueError("Property sdo_service should be only in [Sdoservice.RESPONSE, SdoService.INFO]")

    def parse_response_frame(self, response: bytes):
        def debug_log(s: Structure):
            result = {f[0]: getattr(s, f[0]) for f in s._fields_}
            logger.debug(f"{self.__class__.__name__} {s.__class__.__name__}: {result}")

        _bitarray_response = bitarray()
        _bitarray_response.frombytes(response)

        # Parse EtherCAT header
        ethercat_header = _bitarray_response[
            MailBoxFrameOffsetAddress.ETHERCAT_HEADER.value * 8 : MailBoxFrameOffsetAddress.MAILBOX_HEADER.value * 8
        ]
        self._map_structure(ethercat_header, self.ethercat_header)

        debug_log(self.ethercat_header)

        # Parse Mailbox header
        mailbox_header = _bitarray_response[
            MailBoxFrameOffsetAddress.MAILBOX_HEADER.value * 8 : MailBoxFrameOffsetAddress.COE_HEADER.value * 8
        ]
        self._map_structure(mailbox_header, self.mailbox_header)

        debug_log(self.mailbox_header)

        # Parse CoE header
        coe_header = _bitarray_response[
            MailBoxFrameOffsetAddress.COE_HEADER.value * 8 : MailBoxFrameOffsetAddress.SDO_HEADER.value * 8
        ]
        self._map_structure(coe_header, self.coe_header)

        debug_log(self.coe_header)

        # Parse sdo response data
        if self.sdo_service == SdoService.INFO:
            sdo_header = _bitarray_response[
                MailBoxFrameOffsetAddress.SDO_HEADER.value * 8 : MailBoxFrameOffsetAddress.SDO_DATA.value * 8
            ]
            self._map_structure(sdo_header, self.sdo_header)

            data_body_bitarray = _bitarray_response[MailBoxFrameOffsetAddress.SDO_DATA.value * 8 :]

            self.data_body = data_body_bitarray.tobytes()

        else:
            sdo_header = _bitarray_response[
                MailBoxFrameOffsetAddress.SDO_HEADER.value * 8 : MailBoxFrameOffsetAddress.SDO_DATA.value * 8
            ]
            self._map_structure(sdo_header, self.sdo_header)

            data_body_bitarray = _bitarray_response[MailBoxFrameOffsetAddress.SDO_DATA.value * 8 :]

            self.data_body = data_body_bitarray.tobytes()

        debug_log(self.sdo_header)

    def _map_structure(self, input: bitarray, struct_obj: Structure):
        offset = 0
        if sys.byteorder != input.endian():
            input.bytereverse()
        for item in struct_obj._fields_:
            next_offset = offset + item[2]
            sliced = input[offset:next_offset]
            if sys.byteorder != input.endian():
                sliced.reverse()
            if len(sliced) > 0:
                setattr(struct_obj, item[0], util.ba2int(sliced))
            offset += item[2]


class SDOCommandMessage(SDOMessage):
    sdo_command_data: Structure = field(default=SDOInformationODListRequest(), init=False)

    def __post_init__(self):
        super().__post_init__()

    def make_request_frame(self, increase_session: bool = True) -> bytes:
        # SDO Request message parameter set
        if isinstance(self.sdo_header, SDORequest):
            self.sdo_header.Reserved = 0
            self.sdo_header.CompleteAccess = int(self.complete_access)
            self.sdo_header.CommandSpecifier = self.sdo_command.value
            self.sdo_header.Index = self.index
            self.sdo_header.SubIndex = self.sub_index
            self.sdo_header.Reserved2 = 0
        else:
            TypeError(f"sdo_header should be SDORequest type.")

        sdo_bitarray = self.get_bytes(self.sdo_header)
        if self.sdo_command_data is not None:
            sdo_bitarray.extend(self.get_bytes(self.sdo_command_data))

        logger.debug(
            f"Request Body: {self.sdo_command_data.__class__.__name__}, Index:{hex(self.index)}, Subindex:{hex(self.sub_index)} specified."
        )

        _bitarray = self.make_coe_header(len(sdo_bitarray))
        _bitarray.extend(sdo_bitarray)

        # convert bitarray with bytes data and return
        return _bitarray.tobytes()


class SDORequestInfoMessage(SDOMessage):
    """Build SDO "Info Service Data" frame in SDO information Service Request command"""
    opcode: SdoInfoOpcode = field(default=SdoInfoOpcode.GET_OD_LIST_REQ, init=True)
    sdo_command_data: Structure = field(default=None, init=False)

    def __post_init__(self):
        super().__post_init__()

    def make_request_frame(self, increase_session: bool = True) -> bytes:
        # SDO Request message parameter set
        if isinstance(self.sdo_header, SDOInformationHeader):
            self.sdo_header.Opcode = self.opcode.value
            self.sdo_header.Incomplete = 0
            self.sdo_header.FragmentsLeft = 0
            self.sdo_header.ListType = 0x01
            if isinstance(self.sdo_command_data, SDOInformationODListRequest):
                self.sdo_command_data.ListType = 0x01
            elif isinstance(self.sdo_command_data, SDOInformationDescriptionRequest):
                self.sdo_command_data.Index = self.index
            elif isinstance(self.sdo_command_data, SDOInformationEntryRequest):
                self.sdo_command_data.Index = self.index
                self.sdo_command_data.Subindex = self.sub_index
                self.sdo_command_data.ValueInfo = 0x7F

        else:
            TypeError(f"sdo_header should be SDOInformationHeader type.")

        logger.info(
            f"Request Body: {self.sdo_command_data.__class__.__name__}, Index:{hex(self.index)}, Subindex:{hex(self.sub_index)} specified."
        )

        sdo_bitarray = self.get_bytes(self.sdo_header)
        if self.sdo_command_data is not None:
            sdo_bitarray.extend(self.get_bytes(self.sdo_command_data))

        _bitarray = self.make_coe_header(len(sdo_bitarray))
        _bitarray.extend(sdo_bitarray)

        # convert bitarray with bytes data and return
        return _bitarray.tobytes()
