from typing import AnyStr, Callable, AsyncIterable
import inspect

from .request import Request, ClientDisconnect

Stream = AsyncIterable[AnyStr]
StreamFunc = Callable[[], Stream]


def stream_until_disconnect(req: Request, source: Stream) -> Stream:
    # Yield items from a stream until the client disconnects, then
    # throw an exception into the stream.
    assert inspect.isasyncgen(source)

    async def stream():
        async for item in source:
            if await req.is_disconnected():
                try:
                    await source.athrow(ClientDisconnect)
                except StopAsyncIteration:
                    # May be raised in Python 3.6 if the `source`'s error
                    # handling code did not `yield` anything.
                    pass
            yield item

    return stream()
