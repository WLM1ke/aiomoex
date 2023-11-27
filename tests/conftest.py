import aiohttp
import pytest


@pytest.fixture(name="http_session")
async def create_session():
    async with aiohttp.ClientSession() as session:
        yield session
