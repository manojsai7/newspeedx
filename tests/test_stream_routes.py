import asyncio
import pytest
from aiohttp import web

from Megatron.server.stream_routes import routes


@pytest.fixture
async def aiohttp_app(loop, aiohttp_unused_port):
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    port = aiohttp_unused_port()
    site = web.TCPSite(runner, '127.0.0.1', port)
    await site.start()
    yield f'http://127.0.0.1:{port}'
    await runner.cleanup()


@pytest.mark.asyncio
async def test_root_returns_json(aiohttp_app, aiohttp_client):
    client = await aiohttp_client(web.Application())
    # use the route-definition app instead
    resp = await client.get(aiohttp_app + '/')
    assert resp.status == 200
    data = await resp.json()
    assert 'server_status' in data


@pytest.mark.asyncio
async def test_favicon_not_found(aiohttp_app, aiohttp_client):
    client = await aiohttp_client(web.Application())
    resp = await client.get(aiohttp_app + '/favicon.ico')
    assert resp.status == 404
