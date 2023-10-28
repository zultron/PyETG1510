# This is a sample Python script.
from pyetg1510 import EtherCATMasterConnection, MasterODSpecification, ETG1510Profile, SysLog, LoggingLevel, DiagnosisData
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
            pprint({"PortStatus": data.port_status})
            pprint({"ALStatusCode": data.al_status_code})
            pprint({"ALControl": data.al_control})
            pprint({"ALStatus": data.al_status})
            pprint({"Is Rejected?": data.is_rejected})
            pprint({"Is Updated?": data.is_updated})
        await asyncio.sleep(0.3)


async def get_etg1510_data(etg1510: ETG1510Profile, index: int = 0xA000):
    """Get specified index sdo data"""
    # get SDO data of index default 0xA001.
    sdo:DiagnosisData = await etg1510.get_sdo(index)
    pprint({hex(index): {f.name: getattr(sdo, f.name).value for f in fields(sdo)}})
    pprint({"PortStatus": sdo.port_status})
    pprint({"ALStatusCode": sdo.al_status_code})
    pprint({"ALControl": sdo.al_control})
    pprint({"ALStatus": sdo.al_status})
    pprint({"Is Rejected?": sdo.is_rejected})
    pprint({"Is Updated?": sdo.is_updated})


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
    #asyncio.run(get_etg1510_whole_data(etg1510))
    # get sdo data index 0xa001
    asyncio.run(get_etg1510_data(etg1510, 0xA001))
    # get sdo data cyclically
    #asyncio.run(get_etg1510_data_frequently(etg1510))
