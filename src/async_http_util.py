from typing import List, Optional
import aiohttp
import asyncio
import json


async def async_http_get(session, url, tries_threshold) -> Optional[dict]:
    ''' TODO
    '''
    tries = 0
    while tries < tries_threshold * 2:
        try:
            async with session.get(url, timeout=5) as resp:
                data = await resp.json(content_type=None)
            return data
        except json.decoder.JSONDecodeError:
            tries += 1
            # TODO
            await asyncio.sleep(0.1 * tries)
        except aiohttp.client_exceptions.ClientConnectorError:
            # TODO
            break
    return None


async def async_http_handler(urls: List) -> List[Optional[dict]]:
    ''' TODO
    '''
    urls_len = len(urls)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(async_http_get(session, url, urls_len)))

        res = await asyncio.gather(*tasks)
    # print(ask)
    # print(any(i == None for i in ask))
    # print(len(urls))
    return res


def make_async_http_get(urls: List) -> List[Optional[dict]]:
    ''' TODO
    '''
    return asyncio.run(async_http_handler(urls))
