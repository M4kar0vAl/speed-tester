from collections.abc import Callable

import httpx
import pytest

from speed_tester.dto import RequestResult
from speed_tester.measure_speed import run_one_test

URL = "https://example.test/big.jpg"

type Handler = Callable[[httpx.Request], httpx.Response]


async def run(handler: Handler) -> RequestResult:
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        return await run_one_test(client, URL)


def raising(exc: Exception) -> Handler:
    def handler(_: httpx.Request) -> httpx.Response:
        raise exc

    return handler


async def test_success_counts_downloaded_bytes() -> None:
    result = await run(lambda request: httpx.Response(200, stream=httpx.ByteStream(b"x" * 1000)))

    assert result.success is True
    assert result.bytes_downloaded == 1000
    assert result.elapsed_ms > 0
    assert result.error is None


@pytest.mark.parametrize("status", [404, 500])
async def test_http_error_status_is_failure(status: int) -> None:
    result = await run(lambda request: httpx.Response(status))

    assert result.success is False
    assert result.error is not None
    assert str(status) in result.error


@pytest.mark.parametrize(
    "exc",
    [
        httpx.ReadTimeout("too slow"),
        httpx.ConnectError("refused"),
        RuntimeError("Everything has blown up!"),
    ],
    ids=["timeout", "connection_error", "unexpected_error"],
)
async def test_exception_is_failure_not_crash(exc: Exception) -> None:
    result = await run(raising(exc))

    assert result.success is False
    assert result.error
