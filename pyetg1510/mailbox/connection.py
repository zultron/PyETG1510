"""UDP/IP非同期通信モジュール
"""
import asyncio
from dataclasses import dataclass, field


@dataclass
class Messages:
    send: any = field(init=True)
    receive: any = field(init=False)


class UDPClientConnection:
    def __init__(self, message: Messages, on_con_lost):
        self.message: Messages = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(self.message.send)

    def datagram_received(self, data, addr):
        self.message.receive = data
        self.transport.close()

    def error_received(self, exc):
        print("Error received:", exc)

    def connection_lost(self, exc):
        # self.transport.close()
        self.on_con_lost.set_result(True)


@dataclass
class EtherCATMasterConnection:
    host: str = field(default_factory=str, init=True)
    port: int = field(default=9001, init=True)
    received_data: any = field(default=None, init=False)

    async def send_data(self, message):
        loop = asyncio.get_running_loop()
        on_con_lost = loop.create_future()
        messages = Messages(message)
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPClientConnection(messages, on_con_lost), remote_addr=(self.host, self.port)
        )
        try:
            await asyncio.wait_for(on_con_lost, 3)
            self.received_data = messages.receive
        finally:
            transport.close()
