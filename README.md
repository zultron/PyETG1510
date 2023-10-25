This package is client software that acquire diagnostic information from the EtherCAT master with vendor independent.

Various diagnostic information defined as the ETG.1510 SDO entries at the EtherCAT master, these are possible to be acquired 
via Mailbox Gateway (ETG.8200).

The EtherCAT master supports not a whole OD entries of ETG.1510 specified but a partially by each vendor, further the data size of ``VISIBLE_STRING`` types is not specified on ETG 1510.

Therefore, as first the client has to fetch SDO information by SDO information service due to know these information.

This package has the following features.

1. Acquire object dictionaries (OD) from EtherCAT master by using SDO information service. And makes python dictionary type data with a valid SDO index as the key and SDO container as the value.
2. Acquire diagnosis data from EtherCAT master using based on valid OD entries dictionary.

These data are possible to be acquired by python asynchronous iterator.

## Installation

```shell
$ pip install pyetg1510
```

## Connection

If you want to know connect to Mailbox Gateway host address, Please see homepage.

## Quick start

``` python
# This is a sample Python script.
from pyetg1510 import EtherCATMasterConnection, MasterODSpecification, ETG1510Profile, SysLog, LoggingLevel
from dataclasses import fields
import asyncio
import sys
from socket import inet_aton
from pprint import pprint

async def get_etg1510_whole_data(etg1510: ETG1510Profile):
    """Get whole sdo data one time"""
    # Getting sdo data by ETG.1510 profile generator.
    async for entry, data in etg1510:
        pprint({hex(entry): {f.name: getattr(data, f.name).value for f in fields(data)}})

async def get_etg1510_data_frequently(etg1510: ETG1510Profile):
    """Get selected sdo data cyclically"""
    # Getting sdo data by ETG.1510 profile generator.
    watch_list = list(etg1510.sdo_database.keys())
    # only diagnosis data
    etg1510.watch_index_list = list(filter(lambda x: 0xA000 <= x <= 0xAFFF, watch_list))
    # Getting sdo data by ETG.1510 profile generator.
    while True:
        async for entry, data in etg1510:
            pprint({hex(entry): {f.name: getattr(data, f.name).value for f in fields(data)}})
        await asyncio.sleep(0.3)

async def get_etg1510_data(etg1510: ETG1510Profile, index: int = 0xA000):
    """Get specified index sdo data"""
    # get SDO data of index default 0xA001.
    sdo = await etg1510.get_sdo(index)
    pprint({hex(index): {f.name: getattr(sdo, f.name).value for f in fields(sdo)}})


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    # logging settings
    SysLog.console_log_configuration(LoggingLevel.DISABLE)
    SysLog.syslog_configuration(LoggingLevel.DISABLE)
    SysLog.rotation_log_configuration(LoggingLevel.WARNING)
    SysLog.set_loglevel(LoggingLevel.WARNING)

    # Get target ip address from command argument
    def is_valid_ip(addr):
        try:
            inet_aton(addr)
            return True
        except:
            return False

    args = sys.argv
    if len(args) < 2:
        print("Please specify ip address of mailbox gateway.")
        exit(-1)
    elif not is_valid_ip(args[1]):
        print(f"Wrong ip address has been specified. {args[1]}")
        exit(-1)
    else:
        ipaddress = args[1]

    # UDP/IP communication instance
    connection = EtherCATMasterConnection(ipaddress, 34980)
    # SDO Information service instance
    master_config = MasterODSpecification(connection=connection)
    # ETG.1510 SDO update command generator
    etg1510 = ETG1510Profile(master_od=master_config)
    # As first, getting SDO specification with SDO information service.
    asyncio.run(etg1510.master_od.get_object_dictionary())
    # get whole sdo data on an asynchronous task.
    asyncio.run(get_etg1510_whole_data(etg1510))
    # get sdo data index 0xa001
    asyncio.run(get_etg1510_data(etg1510, 0xA001))
    # get sdo data cyclically
    asyncio.run(get_etg1510_data_frequently(etg1510))
```

This sample would work as below. 

```bash
$ python etg1510.py 192.168.2.254
{'0x1000': {'DeviceType': 0}}
{'0x1008': {'DeviceName': 'TwinCAT EtherCAT Master'}}
{'0x1009': {'HardwareVersion': '0'}}
{'0x100a': {'SoftwareVersion': '3.1 1737'}}
{'0x1018': {'NumberOfEntries': 4,
            'ProductCode': 65539,
            'RevisionNumber': 1737,
            'SerialNumber': 0,
            'VendorID': 2}}
{'0x8000': {'DeviceType': 0,
            'DiagHistoryObjectSupported': False,
            'FixedStationAddress': 1001,
            'Flags': 0,
            'LinkPreset': 17,
            'LinkStatus': 0,
            'MailboxInSize': 0,
            'MailboxOutSize': 0,
            'MailboxProtocolsSupported': 0,
            'Name': 'Term 1 (EK1100)',
            'NumberOfEntries': 37,
            'PortPhysics': 0,
            'ProductCode': 72100946,
            'RevisionNumber': 1114112,
            'SerialNumber': 0,
            'Type': 'EK1100',
            'VendorId': 2}}
{'0x8001': {'DeviceType': 0,
            'DiagHistoryObjectSupported': False,
            'FixedStationAddress': 1002,
            'Flags': 0,
            'LinkPreset': 17,
            'LinkStatus': 0,
            'MailboxInSize': 0,
            'MailboxOutSize': 0,
            'MailboxProtocolsSupported': 0,
            'Name': 'Term 2 (EL1012)',
            'NumberOfEntries': 37,
            'PortPhysics': 0,
            'ProductCode': 66334802,
            'RevisionNumber': 1048576,
            'SerialNumber': 0,
            'Type': 'EL1012',
            'VendorId': 2}}
              :
              :
{'0xa000': {'ALControl': 8,
            'ALStatus': 8,
            'ALStatusCode': 0,
            'AbnormalStateChangeCounter': 0,
            'CyclicWCErrorCounter': 0,
            'DisableAutomaticLinkControl': False,
            'FixedAddressConnPort': [0, 1002, 0, 0],
            'FrameErrorCounterPort': [0, 0, 0, 0],
            'LastProtocolError': 0,
            'LinkConnStatus': 50,
            'LinkControl': 240,
            'NewDiagMessageAvailable': False,
            'NumberOfEntries': 17,
            'SlaveNotPresentCounter': 7}}
{'0xa001': {'ALControl': 8,
            'ALStatus': 8,
            'ALStatusCode': 0,
            'AbnormalStateChangeCounter': 0,
            'CyclicWCErrorCounter': 1,
            'DisableAutomaticLinkControl': False,
            'FixedAddressConnPort': [1001, 1003, 0, 0],
            'FrameErrorCounterPort': [0, 0, 0, 0],
            'LastProtocolError': 0,
            'LinkConnStatus': 51,
            'LinkControl': 240,
            'NewDiagMessageAvailable': False,
            'NumberOfEntries': 17,
            'SlaveNotPresentCounter': 7}}
              :
              :
{'0xf002': {'NumberofEntries': 67,
            'ScanCommandRequest': '\x04\x06',
            'ScanCommandResponse': '',
            'ScanCommandStatus': 0}}
{'0xf020': {'ConfiguredAddress': [1001, 1002, ..., 0], 'NumberofSlaves': 10}}
{'0xf120': {'ACyclicFramesPerSecond': 0,
            'ACyclicLostFrames': 98826091,
            'CyclicFramesPerSecond': 0,
            'CyclicLostFrames': 66,
            'MasterState': 0,
            'NumberOfEntries': 2}}
{'0xf200': {'NumberOfEntries': 1, 'ResetDiagInfo': False}}

```
