'''
Created on 25 apr 2019

@author: Matteo
'''
# Imports
import logging
import asyncio
from . import _LOGGER
from .const import (CD_RETURN_IMMEDIATELY,CD_CONTINUE_WAITING)
from .orvibo_udp import (OrviboUDP,MAGIC,PADDING_1,DISCOVERY_S20,PADDING_2)

STATECHANGE_ID  = b'\x64\x63'
STATECHANGE_LEN = b'\x00\x17'
# Datagram protocol

class S20(OrviboUDP):

    def __init__(self,hp,mac,mytime = None,**kwargs):
        OrviboUDP.__init__(self, hp, mac, mytime, ** kwargs)
        self.state = -1

    def use_subscribe_data(self,s_data):
        self.state = 0 if s_data[-1:]==b'\x00' else 1
        
    def check_statechange_packet(self,data,addr):
        return CD_RETURN_IMMEDIATELY if len(data)>6 and data[4:6] == (STATECHANGE_ID) and self.is_my_mac(data) else CD_CONTINUE_WAITING
    
        
    async def state_change(self,newst):
        if await self.subscribe_if_necessary():
            pkt = MAGIC + STATECHANGE_LEN + STATECHANGE_ID + self.mac + PADDING_1\
                + PADDING_2+(b'\x01' if int(newst) else b'\x00')
            if await self.protocol(pkt,self.hp,self.check_statechange_packet,3,3):
                return True
        return False
    
    @staticmethod
    async def discovery(broadcast_address='255.255.255.255',timeout=5,retries=3):
        disc = await OrviboUDP.discovery(broadcast_address, timeout, retries)
        hosts = dict()
        for k,v in disc.items():
            if v['type']==DISCOVERY_S20:
                hosts[k] = S20(**v)
        return hosts

if __name__ == '__main__': # pragma: no cover
    import sys
    import traceback
    async def testFake(n):
        for i in range(n):
            _LOGGER.debug("Counter is %d",i)
            await asyncio.sleep(1)
    async def discoveryTest():
        v = await S20.discovery('192.168.25.255', 7, 3)
        if v:
            _LOGGER.info("Discovery str %s",v)
        else:
            _LOGGER.warning("Discovery failed")
    
    async def set_state_test(st):
        a = S20(('192.168.25.42',10000),b'\xac\xcf\x23\x93\x34\x9c')
        rv = await a.state_change(st)
        if rv:
            _LOGGER.info("Change state ok")
        else:
            _LOGGER.warning("Change state failed")
    _LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    loop = asyncio.get_event_loop()
    try:
        #loop.run_until_complete(discoveryTest())
        asyncio.ensure_future(testFake(10))
        loop.run_until_complete(set_state_test(0))
    except Exception as ex:
        _LOGGER.error("Test error %s",ex)
        traceback.print_exc()
    finally:
        loop.close()