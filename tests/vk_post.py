import asyncio
import os
import ssl

import aiohttp


def json_factory():
    return {
        'secret': os.environ['VK_SECRET'],
        'type': 'message_new',
        'object': {
            'message': {
                'from_id': 173799769,
                'text': 'сегодня',
            }
        }
    }


def bad_json():
    return {}


def confirmation_json():
    return {'type': 'confirmation', 'group_id': 199932261}


default_ssl = ssl.create_default_context(cafile='schedule/ssl/vkapi.crt')


async def vk_send_message(factory, sslcontext):
    async with aiohttp.ClientSession() as session:
        await session.post('http://localhost:8888', json=factory(), ssl=sslcontext)


if __name__ == '__main__':
    asyncio.run(vk_send_message(json_factory, default_ssl))
