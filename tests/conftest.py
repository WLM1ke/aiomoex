import aiohttp
import pytest


@pytest.fixture(scope="function", name="http_session")
@pytest.mark.asyncio
def create_session():
    session = aiohttp.ClientSession()
    yield session
    session.close()
