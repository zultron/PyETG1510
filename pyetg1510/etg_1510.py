"""

ETG.1510データ収集制御モジュール。 ``sdo_*xxx_`` から始まるモジュールで定義されたメタデータを通じてデータモデルを参照。
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
    """定義された :obj:`メタデータ <pyetg1510.mailbox.sdo_data_factory.SdoMetadata>` とそのインデックス範囲を関連付けるクラス

    ベースクラス :mod:`pyetg1510.mailbox.sdo_data_factory.SdoMetadataMapper.find` メソッドにより何れかのメンバーをセレクトすることができる。
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
    """SDO Information service [#f1]_  により、収集可能な、EtherCAT main device のサポートするSDO情報を管理するクラス。

    .. [#f1] `ETG.1000.6 <https://www.ethercat.org/jp/downloads/downloads_A02E436C7A97479F9261FDFA8A6D71E5.htm>`_ Section 5.6.3

    Args:
        connection(EtherCATMasterConnection): 通信コネクタオブジェクト

    """

    connection: EtherCATMasterConnection
    sdo_data_entity: ConcreteSDODataFactory = field(default_factory=ConcreteSDODataFactory, init=False)

    def __post_init__(self):
        self.data_handler = SdoDataController(session=self.connection, get_info=True)
        self.current_index = 0
        self.current_subindex = 0

    async def get_object_dictionary(self):
        """SDO Information serviceによりmain deviceのODを問い合わせ、その仕様をsdo_data_entryへ登録。

        次の手順で実行する。

        1. OD Listを収集し、 :obj:`メタデータマッパ <pyetg1510.etg_1510.MasterDiagnosisMetadataMapper>` を用いて
           対応する :obj:`メタデータ <pyetg1510.mailbox.sdo_data_factory.SdoMetadata>` を取得
        2. :mod:`ConcreteSDODataFactory` によりテンプレートを元に実体を作成し、sdo_data_entryに登録。
        3. 個々のODのDescriptionを要求し、作成した実体をレスポンスに従い更新。
        4. sdo_data_entryに問い合わせたデータが作成される。

        """
        logger.info("Fetch OD List")
        await self.data_handler.fetch(sdo_metadata=ODListFormat, sdo_data=ODListFormat.response_container())

        for self.current_index in self.data_handler.sdo_data.ObjectIndex.value:
            logger.info(f"==== Index {self.current_index}, format :{ODListFormat.response_container.__name__}")
            _selected: MappingMember = MasterDiagnosisMetadataMapper.find(self.current_index)
            if _selected is not None:
                # Create instances by sdo factory.
                self.sdo_data_entity.create(index=self.current_index, template=_selected.metadata.response_container)
            else:
                logger.warning(f"Index : {self.current_index} is not defined for any specification.")
                continue
            SDOInfoDescriptionFormat.index = self.current_index
            logger.info("Fetch Object Description")
            await self.data_handler.fetch(
                sdo_metadata=SDOInfoDescriptionFormat, sdo_data=SDOInfoDescriptionFormat.response_container()
            )
            # apply max subindex to configuration model
            if hasattr(self.data_handler.sdo_data, "MaxSubindex"):
                _selected.metadata.max_sub_index = self.data_handler.sdo_data.MaxSubindex.value
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
    """ETG.1510 データ収集非同期イテレータ

    master_od にセットしたODリストに従い、順次SDOを収集して返すイテレータクラス。

    使用例:
        .. code-block:: python

            async def get_sdo_data():
                # create iterator object
                ittr = ETG1510Profile(master_od=<<MasterConfigurationクラスで作成したODデータモデル>>)
                async for sdo in ittr:
                    # sdo will be possible to get each SDO as SdoDataBody type or Dictionary type.
                    pass

    Args:
        master_od(MasterODSpecification): :meth:`get_object_dictionaryメソッド <pyetg1510.etg_1510.MasterODSpecification.get_object_dictionary>`
                                        を実行してODを収集完了した後のMasterODSpecificationオブジェクト
        watch_index_list(List[int]): 監視対象のSDOインデックスリスト。未定義の場合はOD全て対象。

    Return:
        Tuple[int, SdoDataBody]: SDOインデックス, 取得したSDOデータコンテナ
    """

    master_od: MasterODSpecification
    """収集したメインデバイスのオブジェクトディクショナリ"""
    watch_index_list: List[int] = None
    """イテレータで収集する際に、収集対象となるインデックスリストを指定する場合はそのリストを設定する。指定しない場合は全て返す"""

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
        """
        指定したインデックスのSDOを取得する

        Args:
            index(int): SDOインデックス

        Return:
            SdoDataBody: 取得したSDOデータコンテナ
        """

        sdo_metadata = MasterDiagnosisMetadataMapper.find(index).metadata
        sdo_metadata.index = index
        await self.data_handler.fetch(sdo_metadata=sdo_metadata, sdo_data=self.sdo_database[index])

        return self.data_handler.sdo_data
