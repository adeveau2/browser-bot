"""

Sample bot that returns results from both Sage and Claude-Instant.

"""
from __future__ import annotations

from typing import AsyncIterable
import asyncio

from fastapi_poe import PoeBot, run
from fastapi_poe.client import MetaMessage, stream_request
from fastapi_poe.types import QueryRequest
from sse_starlette.sse import ServerSentEvent
from urlextract import URLExtract
import requests
import time
import aiohttp
from cache import AsyncLRU



DIFF_BOT_API_KEY = "fe2697966b4353f314fb461ededc394d"


def replace_urls(s, url_map):
    for url in url_map:
        s = s.replace(url, url_map[url])
    return s

@AsyncLRU(maxsize=128)
async def extract_using_diffbot(url):

    api_endpoint = f"https://api.diffbot.com/v3/analyze?url={url}&token={DIFF_BOT_API_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_endpoint) as response:
            html = await response.json()
    try:
        return  {url: html.get('objects')[0].get('text')[:2000]}
    except:
        return {}

class SummaryBot(PoeBot):

    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:
        urls = [url for x in query.query for url in URLExtract().find_urls(x.content)]


        tasks = [asyncio.create_task(extract_using_diffbot(url)) for url in urls]
        i = 0
        while True:
            done, pending = await asyncio.wait(tasks, timeout = 1)
            if i > 2:
                yield self.replace_response_event("Reading" + "."*(i % 4))
            if not pending:
                break
            i += 1


        urls_map = {}
        while done:
            urls_map.update(done.pop().result())

        if i != 0:
            yield self.replace_response_event("\n")
    
        new_query = query.copy(
            update={"query": [x.copy(update = {"content": replace_urls(x.content, urls_map)}) for x in query.query]}
        )

        async for msg in stream_request(new_query, "sage", new_query.api_key):
            if isinstance(msg, MetaMessage):
                continue
            elif msg.is_suggested_reply:
                yield self.suggested_reply_event(msg.text)
            elif msg.is_replace_response:
                yield self.replace_response_event(msg.text)
            else:
                yield self.text_event(msg.text)


if __name__ == "__main__":
    run(SummaryBot())
