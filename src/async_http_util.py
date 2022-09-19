from typing import List, Optional
import aiohttp
import asyncio


async def async_http_get(session, url) -> Optional[dict]:
    ''' TODO
    '''
    async with session.get(url, timeout=5) as resp:
        data = await resp.json()
    return data


async def async_http_handler(urls: List) -> List[Optional[dict]]:
    ''' TODO
    '''
    async with aiohttp.ClientSession() as session:

        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(async_http_get(session, url)))

        ask = await asyncio.gather(*tasks)
    # print(ask)
    return ask


def make_async_http_get(urls: List) -> List[Optional[dict]]:
    ''' TODO
    '''
    return asyncio.run(async_http_handler(urls))
