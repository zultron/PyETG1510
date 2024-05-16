"""
SDO data generation module
"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, asdict, field
import dataclasses
from typing import Dict, Generic, TypeVar, Tuple
from struct import calcsize, unpack_from, unpack, error
from ctypes import Structure
from pyetg1510.helper import SysLog
from .connection import EtherCATMasterConnection
from .mailbox_gateway import (
    SDOInformationODListRequest,
    SDOInformationEntryRequest,
    SDOInformationDescriptionRequest,
    SDOResponseMessage,
    SdoService,
    SDORequestInfoMessage,
    SdoInfoOpcode,
    SDOCommandMessage,
)

logger = SysLog.logger

T = TypeVar("T")
is_primitive = lambda x: isinstance(x, (int, float, bool, str))


@dataclass
class AbstructSdoDataBody(metaclass=ABCMeta):
    """SDODataBody interface"""

    def __new__(cls, *args, **kwargs):
        dataclass(cls)
        return super().__new__(cls)

    @property
    @abstractmethod
    def unpack_format(self):
        """unpack format abstract method"""
        pass

    @property
    @abstractmethod
    def total_size(self):
        """total size property get"""
        pass


class SDODataFactory(metaclass=ABCMeta):
    """SDO Data Factory Abstract Class"""

    def create(self, index: int, template: AbstructSdoDataBody.__class__):
        """SDO data generation method

         Abstract class that generates a `SDODataBody` object and registers it
         in the dictionary corresponding to the index

         Args:
             index(int): SDO index
             template(AbstructSdoDataBody.__class__): defined in
               :obj:`<pyetg1510.mailbox.sdo_data_factory.SdoMetadata>` defined
               in response_container Template class
               :obj:`<pyetg1510.mailbox.sdo_data_factory.SdoMetadata.response_container>`
        """
        p = self.createProduct(template)
        self.registerProduct(index, p)
        return p

    @abstractmethod
    def createProduct(self, template: AbstructSdoDataBody.__class__):
        pass

    @abstractmethod
    def registerProduct(self, index: int, product):
        pass


@dataclass
class ConcreteSDODataFactory(SDODataFactory):
    """SDO Data Factory concrete class"""

    entries: Dict[int, AbstructSdoDataBody] = field(default_factory=dict, init=False)
    """object dictionary
        
    Args:
        (int): SDO index
        (SdoDataBody): SDO data object
    """

    def createProduct(self, template: AbstructSdoDataBody.__class__):
        """Create instance from template class

        Args:
            template(class): template class

        Return:
            SDODataBody: Generated instance
        """
        return template()

    def registerProduct(self, index: int, product: AbstructSdoDataBody):
        """Register SDODataBody objects for each index"""
        self.entries[index] = product


@dataclass
class SdoEntry(Generic[T]):
    """SDO data container

    Since it has a generic type variable, the type must be specified when
    defining an instance.
    """

    name: str = field(default_factory=str, init=False)
    """SDO Entry name"""
    sub_index: int
    """SDO sub index"""
    value: T
    """SDO value"""
    format: str
    """
    struct.unpack format specification string
    
    https://docs.python.org/ja/3/library/struct.html#format-characters
    """
    size: int = field(default=None, init=True)
    """Data size (Byte)

    The meaning of the size to be specified differs depending on the data type.

    primitive type::
        :mod:`format` で指定したサイズ。例えば5つの連続した32bit整数であればformatには ``5I`` と指定され、サイズは5 x 4 = 20byteが得られる。
    collection type:
        Element count * :mod:`format` size specifier
    """
    enable: bool = field(default=False, init=True)
    """Enabled flag by SDO information service"""

    def __post_init__(self):
        if self.size is None:
            if is_primitive(self.value):
                self.size = calcsize(self.format)
            else:
                self.size = len(self.value) * calcsize(self.format)


@dataclass
class SdoDataBody(AbstructSdoDataBody):
    """SDODataBody implementation class

    Raises:
        TypeError:  Occurs when registering a member other than SdoEntry
    """

    def __post_init__(self):
        for each_field in self.__annotations__.items():
            if not issubclass(each_field[1], SdoEntry):
                raise TypeError(
                    "Can't define as field except 'SdoDataBody'."
                    f" Actual {each_field[0]} : {each_field[1]}"
                )
        # self.sub_index_dic = {asdict(self)[k]['sub_index']: k for k in asdict(self)}

    @property
    def unpack_format(self) -> str:
        """Generate format for struct.unpack"""
        # If the size of the element of data is larger than the specified size
        # of the format, add the specified size number to the beginning
        result = "="
        for field in dataclasses.fields(self):
            entry = getattr(self, field.name)
            temp = ""
            format_size = calcsize(entry.format)
            if not entry.enable:
                continue
            if is_primitive(entry.value):
                # for primitive entry value
                logger.debug(f"{entry.value} : is primitive.")
                if format_size < entry.size:
                    temp += str(int(entry.size / format_size)) + entry.format
                else:
                    temp += entry.format
            elif hasattr(entry.value, "__iter__"):
                # for iterable object entry
                temp += str(int(entry.size / format_size)) + entry.format
                logger.debug(
                    f"{entry.value} : is NOT primitive. size :{entry.size},"
                    f" format size: {format_size}, format: {temp}"
                )
            else:
                temp += entry.format
            if calcsize(result) % 2 == 0 or calcsize(result + temp) % 2 == 0:
                result += temp
            else:
                result += "x" + temp
        return result

    @property
    def total_size(self) -> int:
        return sum([getattr(self, f.name).size for f in dataclasses.fields(self) if getattr(self, f.name).enable])

    @property
    def values(self):
        dict_value = asdict(self)
        return {f: dict_value[f]["value"] for f in dict_value}

    def set_value(self, sub_index: int, value: SdoEntry):
        # sub_index_dic = {asdict(self)[k]['sub_index']: k for k in asdict(self)}
        # if sub_index in sub_index_dic:
        #    setattr(self, sub_index_dic[sub_index], value)
        # else:
        #    raise ValueError(f"No such subindex :{sub_index}")
        for item in dataclasses.fields(self):
            if getattr(self, item.name).sub_index == sub_index:
                setattr(self, item.name, value)
        raise ValueError(f"No such subindex :{sub_index}")

    def get_value(self, sub_index: int) -> SdoEntry:
        for item in dataclasses.fields(self):
            print(getattr(self, item.name).sub_index)
            if getattr(self, item.name).sub_index == sub_index:
                return getattr(self, item.name)

        raise ValueError(f"No such sub index :{sub_index}, attribute: {item.name}, class:{self.__class__.__name__}")


@dataclass
class SdoMetadata:
    """SDO metadata"""

    index: int
    """index number"""
    sub_index: int
    """sub index number"""
    support_complete_access: bool
    """complete access possible entry"""
    max_sub_index: int
    """Maximum subindex number"""
    request_container: Structure.__class__
    """Define a container class with ctype.Structure as the base class to store the
    request data of the upload command."""
    response_container: SdoDataBody.__class__
    """Define a container class with SdoDataBody as a base class to store the
    response data of the upload command."""


@dataclass
class MappingMember:
    """OD mapping definition object"""

    index_range: Tuple[int, int]
    """OD index range"""
    metadata: SdoMetadata
    """ SDO metadata :obj:`<pyetg1510.mailbox.sdo_data_factory.SdoMetadata>` """


class SdoMetadataMapper:
    """SDO data mapping class"""

    def __post_init__(self):
        """メンバにMappingMember以外のデータが含まれていたらValueErrorとする"""
        for each_field in self.__annotations__.items():
            if not issubclass(each_field[1], MappingMember):
                raise TypeError(
                    f"Can't define as field except '{MappingMember.__class__.__name__}'. Actual {each_field[0]} : {each_field[1]}"
                )

    @classmethod
    def find(cls, index: int) -> MappingMember:
        """Returns the OD mapping definition object according to the specified index

         Args:
             index(int): SDO index number

         Return:
             MappingMember: OD mapping definition object
        """
        for field in vars(cls):
            if isinstance(vars(cls)[field], MappingMember):
                index_range = vars(cls)[field].index_range
                if index_range[0] <= index <= index_range[1]:
                    return vars(cls)[field]
        return None

    @classmethod
    def find_start(cls, index: int):
        return cls.find(index).index_range[0]


class ODList(SdoDataBody):
    """OD list members"""
    ListType: SdoEntry = field(
        default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H", enable=True))
    ObjectIndex: SdoEntry = field(
        default_factory=lambda: SdoEntry(sub_index=0, value=[0], format="H", enable=True)
    )


ODListFormat = SdoMetadata(
    index=-1,
    sub_index=-1,
    support_complete_access=False,
    max_sub_index=0,
    request_container=SDOInformationODListRequest,
    response_container=ODList,
)


class SDOInfoDescription(SdoDataBody):
    """Detailed information for individual SDO Index"""
    Index: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H", enable=True))
    DataType: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H", enable=True))
    MaxSubindex: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B", enable=True))
    ObjectCode: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B", enable=True))
    Name: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=0, value="", format="s", enable=True))


SDOInfoDescriptionFormat = SdoMetadata(
    index=0,
    sub_index=-1,
    support_complete_access=False,
    max_sub_index=0,
    request_container=SDOInformationDescriptionRequest,
    response_container=SDOInfoDescription,
)


class SDOInfoEntry(SdoDataBody):
    """Detailed information for individual SDO Index"""
    Index: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H", enable=True))
    Subindex: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B", enable=True))
    ValueInfo: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="B", enable=True))
    DataType: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H", enable=True))
    BitLength: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H", enable=True))
    ObjectAccess: SdoEntry = field(
        default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="H", enable=True)
    )
    Data: SdoEntry = field(default_factory=lambda: SdoEntry[str](sub_index=0, value="", format="s", enable=True))


SDOInfoEntryFormat = SdoMetadata(
    index=0,
    sub_index=0,
    support_complete_access=False,
    max_sub_index=0,
    request_container=SDOInformationEntryRequest,
    response_container=SDOInfoEntry,
)


class SDOInfoError(SdoDataBody):
    AbortCode: SdoEntry = field(default_factory=lambda: SdoEntry[int](sub_index=0, value=0, format="I", enable=True))


SDOInfoErrorFormat = SdoMetadata(
    index=0,
    sub_index=0,
    support_complete_access=False,
    max_sub_index=0,
    request_container=None,
    response_container=SDOInfoError,
)


@dataclass
class SdoDataController:
    """SDO message service

    Args:
        session(EtherCATMasterConnection): communication connector object
        get_info(bool): Set `True` to query SDO Information service
    """

    session: EtherCATMasterConnection
    sdo_data: SdoDataBody = field(default=None)
    get_info: bool = field(default=False)

    def __post_init__(self):
        self.data_body_size: int = 0
        self.index_counter: int = 0

    def _map(self, raw_data: bytes):
        """Map SDO data body part to internal model

        Unpack the received byte data and create SdoFormat with
        :meth:`get_object_dictionary
        <pyetg1510.etg_1510.MasterODSpecification.get_object_dictionary>`

        Args:
            raw_data(bytes): Data body part of response data received by Upload command
            self.sdo_data(SdoDataBody): Data container to map to
        Raises:
            TypeError: If the format specification in struct.unpack is invalid
                or the size does not match
            struct.error: If struct.unpack processing fails
        """
        logger.info(self.sdo_data)
        logger.info(
            f"Before adjusting size, Unpack format:{self.sdo_data.unpack_format},"
            f" format size:{calcsize(self.sdo_data.unpack_format)},"
            f" Setting size: {self.sdo_data.total_size},"
            f" Actual size: {len(raw_data)}"
        )
        if self.sdo_data.total_size < len(raw_data):
            lastkey = next(reversed(asdict(self.sdo_data)), None)
            current_value = getattr(self.sdo_data, lastkey)
            current_value.size += len(raw_data) - self.sdo_data.total_size
            setattr(self.sdo_data, lastkey, current_value)
        unpack_format = self.sdo_data.unpack_format
        format_size = calcsize(unpack_format)
        if format_size <= 0:
            raise ValueError("All member are disabled."
                             f" ({unpack_format}) Nothing to fetch data.")

        logger.info(
            f"Unpack format: {unpack_format}, Unpack size: {format_size},"
            f"Calculated size: {self.sdo_data.total_size},"
            f" raw bytes data size : {len(raw_data)}"
        )
        if len(raw_data) < format_size:
            logger.error(f"Data: {raw_data}, Unpack format: {unpack_format}")
            raw_data += b"\0" * (format_size - len(raw_data))
            # raise ValueError(f"Required data size at least {format_size} byte. actual: {len(raw_data)} byte")
        try:
            _data = list(unpack(unpack_format, raw_data))
        except error as e:
            logger.exception(
                f"unpack error: unpack format size: {calcsize(unpack_format)},"
                f"data size: {len(raw_data)}\n"
                f"    Specified datamodel: {self.sdo_data}\n"
            )

            raise
        _data = [f.strip(b"\0").decode() if type(f) is bytes else f for f in _data]
        sdo_data_dict = asdict(self.sdo_data)
        sdo_data_dict = {k: sdo_data_dict[k]
                         for k in sdo_data_dict
                         if sdo_data_dict[k]["enable"]}
        if len(sdo_data_dict) > len(_data):
            raise ValueError(
                f"Mismatching configured SDO data number and received data.\n"
                f"    Received data: count: {len(_data)},"
                f" unpack format {unpack_format}, Unpack data: {_data}\n"
                f"    Configured model: count: {len(sdo_data_dict)},"
                f" model:{sdo_data_dict}"
            )
        k = 0
        i = 0
        for key in sdo_data_dict:
            if is_primitive(getattr(self.sdo_data, key).value):
                value = getattr(self.sdo_data, key)
                value.value = _data[i]
                setattr(self.sdo_data, key, value)
                i += 1
            elif type(getattr(self.sdo_data, key).value) is type(_data):
                byte_size = getattr(self.sdo_data, key).size
                list_size = int(byte_size /
                                calcsize(getattr(self.sdo_data, key).format))
                set_list = _data[i : i + list_size]
                value = getattr(self.sdo_data, key)
                value.value = set_list
                setattr(self.sdo_data, key, value)
                i += len(set_list)
            else:
                raise TypeError(
                    f"Type unmatched. \n {self.sdo_data[key].name} :type(self.sdo_data[key].value)\n specified:{type(_data[i])}"
                )

            k += 1

    def _object_initialization(self, sdo_metadata: SdoMetadata):
        """リクエスト、レスポンス各メッセージコンテナを初期化する。"""

        if self.get_info:
            self.response_message = SDOResponseMessage(sdo_service=SdoService.INFO)
            self.request_message = SDORequestInfoMessage(sdo_service=SdoService.INFO)
            if sdo_metadata == ODListFormat:
                logger.info("Fetching OD List")
                self.request_message.opcode = SdoInfoOpcode.GET_OD_LIST_REQ
            elif sdo_metadata == SDOInfoDescriptionFormat:
                logger.info("Fetching Object Description")
                self.request_message.opcode = SdoInfoOpcode.GET_DESCRIPTION_REQ
            elif sdo_metadata == SDOInfoEntryFormat:
                logger.info("Fetching Entry Description")
                self.request_message.opcode = SdoInfoOpcode.GET_ENTRY_REQ
        else:
            self.response_message = SDOResponseMessage(sdo_service=SdoService.RESPONSE)
            self.request_message = SDOCommandMessage(sdo_service=SdoService.REQUEST)

        self.request_message.sdo_command_data = sdo_metadata.request_container()

    async def fetch(self, sdo_metadata: SdoMetadata, sdo_data: SdoDataBody):
        """Issue an SDO Upload request and map to the SdoDataBody model

        Args:
            sdo_metadata(SdoMetaData): SDO Metadata
               :obj:`<pyetg1510.mailbox.sdo_data_factory.SdoMetadata>`
            sdo_data(SdoDataBody): Container object that stores received SDO data
        """
        self.sdo_data = sdo_data
        self._object_initialization(sdo_metadata=sdo_metadata)
        self.request_message.index = sdo_metadata.index
        self.request_message.sub_index = sdo_metadata.sub_index
        self.request_message.complete_access = sdo_metadata.support_complete_access

        logger.debug(
            f"Command to be requested index:{self.request_message.index},"
            f"subindex: {self.request_message.sub_index},"
            f"complete access: {self.request_message.complete_access}"
        )
        # request and wait response

        await self.session.send_data(self.request_message.make_request_frame())
        # parse until CoE header message
        self.response_message.parse_response_frame(self.session.received_data)

        # Parse SDO message
        # 1. Make sure data size either specified size or default size by
        #    SizeIndicator
        # 2. If SizeIndicator is True and expedited bit is True, data size is
        #    specified at 2bit.
        data_body_offset = 0
        sdo_header = self.response_message.sdo_header
        data_body = self.response_message.data_body
        if ("SizeIndicator" in [f[0] for f in sdo_header._fields_]
            and sdo_header.SizeIndicator == 1
        ):
            if sdo_header.TransferType == 1:
                # case : SDO upload expedited response]
                self.data_body_size = 4 - sdo_header.DataSetSize
                logger.debug(
                    "Expedited : True,"
                    f"size specified: {sdo_header.DataSetSize},"
                    f"Calculated size:{self.data_body_size}"
                )
            else:
                temp = unpack_from("@I", data_body, 0)
                self.data_body_size = temp[0]
                data_body_offset = 4
        else:
            self.data_body_size = 4
        if len(data_body[data_body_offset:]) < self.data_body_size:
            logger.warning("!!!STOP!!! Size too low")
            self.index_counter = 0
            raise StopAsyncIteration()
        # SDO Information service checkking Opcode
        if self.get_info and (
            "Opcode" in [f[0] for f in sdo_header._fields_]
            and sdo_header.Opcode == SdoInfoOpcode.SDO_INFO_ERR_REQ.value
        ):
            self.sdo_data = SDOInfoErrorFormat.response_container()
            sdo_metadata = SDOInfoErrorFormat

        # Mapping SDO data body to native model
        # try:
        logger.debug(f"SDO Body message {data_body[data_body_offset:]}")
        self._map(raw_data=data_body[data_body_offset:])
        logger.debug(f"mapped data: {self.sdo_data}")
        # except (ValueError, TypeError, TimeoutError,
        #         asyncio.exceptions.CancelledError,
        #         asyncio.exceptions.InvalidStateError) as e:
        #    logger.warning(e)
        #    self.index_counter = 0
        #    raise StopAsyncIteration()
        logger.debug(
            f"Sequence number: {hex(sdo_metadata.index)}:"
            f"{hex(sdo_metadata.sub_index)} / {self.index_counter}"
        )
        self.index_counter += 1
        # return copy.deepcopy(self.sdo_data)
