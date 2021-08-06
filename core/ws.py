import asyncio
import websockets
import logging
import os

# reading .env file


websocket_url = os.environ['WEBSOCKET_URL']

logger = logging.getLogger(__name__)

def sendUpdate(user, message, id):
    try:
        async def hello(uri):
            async with websockets.connect(uri) as websocket:
                await websocket.send('{"message":"%s"}' % message)
                await websocket.recv()

        def get_or_create_eventloop():
            try:
                return asyncio.get_event_loop()
            except RuntimeError as ex:
                if "There is no current event loop in thread" in str(ex):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return asyncio.get_event_loop()

        get_or_create_eventloop().run_until_complete(
            hello((websocket_url+'%s/') % str(str(user) + str(id)) ))
    except Exception as e:
        logger.debug(str(e))


def sendBroadcast(message):
    try:
        async def hello(uri):
            async with websockets.connect(uri) as websocket:
                await websocket.send('{"message":"%s"}' % message)
                await websocket.recv()

        def get_or_create_eventloop():
            try:
                return asyncio.get_event_loop()
            except RuntimeError as ex:
                if "There is no current event loop in thread" in str(ex):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return asyncio.get_event_loop()

        get_or_create_eventloop().run_until_complete(
            hello(websocket_url+'broadcast/'))
    except Exception as e:
        logger.debug(str(e))
