# python-orvibo

Control Orvibo devices with Python 3 using asyncio (single threaded with event loop). Currently supports the S20 WiFi Smart Switch and AllOne IR.

## Usage

```python
from asyncio_orvibo import S20
import asyncio
import traceback
async def test_switch_all_off_on()
    dict_devices = await S20.discover()
    for _,s in dict_devices.items():
        if await s.state_change(0):
            print("State off OK %s",s)
        else:
            print("State off FAIL %s",s)
    await asyncio.sleep(5)
    for _,s in dict_devices.items():
        if await s.state_change(1):
            print("State on OK %s",s)
        else:
            print("State on FAIL %s",s)
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(test_switch_all_off_on())
except:
    traceback.print_exc()
    
################################################

from asyncio_orvibo import AllOne
import asyncio
import traceback
import binascii
async def test_emit(k)
    dict_devices = await AllOne.discover()
    payload = binascii.unhexlify(k)
    for _,a in dict_devices.items():
        rv = await a.emit_ir(payload)
        if rv:
            print("Emit OK %s %s",a,binascii.hexlify(rv).decode('utf-8'))
        else:
            print("Emit failed")
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(test_emit('00000000a801000000000000000098018e11951127029b0625029906270299062702380227023a0225023802270238022d023202270299062702990627029806270238022702380227023802270238022802370227023802270238022702980627023802240245021c02380227023802270238022702980627029c0623023802270298062702990627029b062502990627029906270220b7a1119d11270299062702990628029b06250238022702380227023802270238022702380227029906270299062702990627023802270238022a0234022702380227023802260238022702380226029a06260238022602380226023802260241021e02380227029b0624029906270238022702980627029b0625029906270299062702990629021db79f11a2112502990627029b0625029906270238022702380227023802270238022a02350227029906270299062702990628023702260238022702380227023802270238022702380226023b02240299062702380226023802270238022602380227023c0223029906270299062702380226029b062402990627029906270299062802980627020000'))
except:
    traceback.print_exc()
```

## Contributions

Pull requests are welcome. Possible areas for improvement:

* Additional Orvibo devices (CT10 for example, I have reverse engineered this device I only need time to write the code).
* Expand S20 functions: Timers, configuration, etc

## Disclaimer

Not affiliated with Shenzhen Orvibo Electronics Co., Ltd.