import json
import aiohttp
import asyncio
import logging
from typing import List, Optional


async def async_http_get(session, url, tries_threshold) -> Optional[dict]:
    ''' Async HTTP GET receiver.
    '''
    tries = 0
    while tries < tries_threshold * 2:
        try:
            async with session.get(url, timeout=5) as resp:
                data = await resp.json(content_type=None)
            return data
        except json.decoder.JSONDecodeError:
            logging.info(f'Not able to get valid JSON data for {url} Retrying...')
            tries += 1
            # Add delay for task to distribute load in time.
            await asyncio.sleep(0.1 * tries)
        except (aiohttp.client_exceptions.ClientConnectorError, asyncio.exceptions.TimeoutError):
            # In case of some connection problem.
            logging.warning(f'Not able to connect: {url}')
            break
    logging.warning(f'Not able to get valid JSON data for {url}')
    return None


async def async_http_handler(urls: List) -> List[Optional[dict]]:
    ''' Main async handler for HTTP GET requests.
    '''
    urls_len = len(urls)
    logging.info(f'Start getting HTTP data for {urls_len} request(s).')

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.create_task(async_http_get(session, url, urls_len)))

        res = await asyncio.gather(*tasks)
    return res


def make_async_http_get(urls: List) -> List[Optional[dict]]:
    ''' Main function to perform async http GET queries.
    '''
    return asyncio.run(async_http_handler(urls))
