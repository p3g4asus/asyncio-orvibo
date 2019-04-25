""" taken from https://gist.github.com/vxgmichel/e47bff34b68adb3cf6bd4845c4bed448
Provide high-level UDP endpoints for asyncio.
Example:
async def main():
    # Create a local UDP enpoint
    local = await open_local_endpoint('localhost', 8888)
    # Create a remote UDP enpoint, pointing to the first one
    remote = await open_remote_endpoint(*local.address)
    # The remote endpoint sends a datagram
    remote.send(b'Hey Hey, My My')
    # The local endpoint receives the datagram, along with the address
    data, address = await local.receive()
    # This prints: Got 'Hey Hey, My My' from 127.0.0.1 port 8888
    print(f"Got {data!r} from {address[0]} port {address[1]}")
"""

import asyncio
import time
from . import _LOGGER
from .const import (CD_ADD_AND_CONTINUE_WAITING,CD_RETURN_IMMEDIATELY)


class DatagramEndpointProtocol(asyncio.DatagramProtocol):
    """Datagram protocol for the endpoint high-level interface."""

    def __init__(self, endpoint):
        self._endpoint = endpoint

    # Protocol methods

    def connection_made(self, transport):
        self._endpoint._transport = transport

    def connection_lost(self, exc):
        if exc is not None:  # pragma: no cover
            msg = 'Endpoint lost the connection: {!r}'
            _LOGGER.warning(msg.format(exc))
        self._endpoint.close()

    # Datagram protocol methods

    def datagram_received(self, data, addr):
        self._endpoint.feed_datagram(data, addr)

    def error_received(self, exc):
        msg = 'Endpoint received an error: {!r}'
        _LOGGER.warning(msg.format(exc))


# Enpoint classes

class Endpoint:
    """High-level interface for UDP enpoints.
    Can either be local or remote.
    It is initialized with an optional queue size for the incoming datagrams.
    """

    def __init__(self, queue_size=None):
        if queue_size is None:
            queue_size = 0
        self._queue = asyncio.Queue(queue_size)
        self._closed = False
        self._transport = None

    # Protocol callbacks

    def feed_datagram(self, data, addr):
        try:
            self._queue.put_nowait((data, addr))
        except asyncio.QueueFull:
            _LOGGER.warning('Endpoint queue is full')

    def close(self):
        # Manage flag
        if self._closed:
            return
        self._closed = True
        # Wake up
        if self._queue.empty():
            self.feed_datagram(None, None)
        # Close transport
        if self._transport:
            self._transport.close()

    # User methods
    
    async def protocol(self,data,addr,check_data_fun,timeout,retry=3):
        lstdata = []        
        for _ in range(retry):
            if data:
                self.send(data,addr)
            starttime = time.time()
            passed = 0
            while passed<timeout:
                try:
                    (rec_data,rec_addr) = await asyncio.wait_for(self.receive(), timeout-passed)
                    rv = check_data_fun(rec_data,rec_addr) 
                    if rv==CD_RETURN_IMMEDIATELY:
                        return rec_data,rec_addr
                    elif rv==CD_ADD_AND_CONTINUE_WAITING:
                        lstdata.append((rec_data,rec_addr))
                except asyncio.TimeoutError as ex:
                    _LOGGER.warning("Protocol timeout %s",ex)
                    break
                passed = time.time()-starttime
            if lstdata:
                return lstdata
            elif not data:
                break
        return None

    def send(self, data, addr):
        """Send a datagram to the given address."""
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.sendto(data, addr)

    async def receive(self):
        """Wait for an incoming datagram and return it with
        the corresponding address.
        This method is a coroutine.
        """
        if self._queue.empty() and self._closed:
            raise IOError("Enpoint is closed")
        data, addr = await self._queue.get()
        if data is None:
            raise IOError("Enpoint is closed")
        return data, addr

    def abort(self):
        """Close the transport immediately."""
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.abort()
        self.close()

    # Properties

    @property
    def address(self):
        """The endpoint address as a (host, port) tuple."""
        return self._transport._sock.getsockname()

    @property
    def closed(self):
        """Indicates whether the endpoint is closed or not."""
        return self._closed


class LocalEndpoint(Endpoint):
    """High-level interface for UDP local enpoints.
    It is initialized with an optional queue size for the incoming datagrams.
    """
    pass


class RemoteEndpoint(Endpoint):
    """High-level interface for UDP remote enpoints.
    It is initialized with an optional queue size for the incoming datagrams.
    """

    def send(self, data):
        """Send a datagram to the remote host."""
        super().send(data, None)

    async def receive(self):
        """ Wait for an incoming datagram from the remote host.
        This method is a coroutine.
        """
        data, addr = await super().receive()
        return data


# High-level coroutines

async def open_datagram_endpoint(
        host, port, *, endpoint_factory=Endpoint, remote=False, **kwargs):
    """Open and return a datagram endpoint.
    The default endpoint factory is the Endpoint class.
    The endpoint can be made local or remote using the remote argument.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    loop = asyncio.get_event_loop()
    endpoint = endpoint_factory()
    kwargs['remote_addr' if remote else 'local_addr'] = host, port
    kwargs['protocol_factory'] = lambda: DatagramEndpointProtocol(endpoint)
    await loop.create_datagram_endpoint(**kwargs,reuse_address=True, reuse_port=None)
    return endpoint


async def open_local_endpoint(
        host='0.0.0.0', port=0, *, queue_size=None, **kwargs):
    """Open and return a local datagram endpoint.
    An optional queue size arguement can be provided.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    return await open_datagram_endpoint(
        host, port, remote=False,
        endpoint_factory=lambda: LocalEndpoint(queue_size),
        **kwargs)


async def open_remote_endpoint(
        host, port, *, queue_size=None, **kwargs):
    """Open and return a remote datagram endpoint.
    An optional queue size arguement can be provided.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    return await open_datagram_endpoint(
        host, port, remote=True,
        endpoint_factory=lambda: RemoteEndpoint(queue_size),
        **kwargs)
