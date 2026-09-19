from collections.abc import Callable

import httpx
import pytest

import speed_tester.measure_speed as ms
from speed_tester.dto import RequestResult, SpeedTestRequest

MIB = 1024 * 1024
URL = "https://example.test/big.jpg"

type FakeRunOneTest = Callable[[list[RequestResult]], list[str]]


@pytest.fixture
def patch_run_one_test(monkeypatch: pytest.MonkeyPatch) -> FakeRunOneTest:
    """
    Factory: Replaces run_one_test with the given results.

    Returns a list of urls with which run_one_test was called.
    """

    def _patch_run_one_test(results: list[RequestResult]) -> list[str]:
        it = iter(results)
        calls: list[str] = []

        async def fake(client: httpx.AsyncClient, url: str) -> RequestResult:
            calls.append(url)
            return next(it)

        monkeypatch.setattr(ms, "run_one_test", fake)
        return calls

    return _patch_run_one_test


async def test_metrics_are_computed_from_successful_requests_only(
        patch_run_one_test: FakeRunOneTest,
):
    patch_run_one_test([
        RequestResult(success=True, bytes_downloaded=1 * MIB, elapsed_ms=500),
        RequestResult(success=True, bytes_downloaded=3 * MIB, elapsed_ms=1500),
        RequestResult(success=False, error="error"),
    ])

    resp = await ms.measure_speed(SpeedTestRequest(url=URL, tries=3))

    assert len(resp.success_results) == 2
    assert len(resp.failure_results) == 1
    assert resp.avg_request_time_ms == pytest.approx(1000)
    assert resp.bytes_downloaded == 4 * MIB
    assert resp.speed_mb_per_s == pytest.approx(2.0)  # 4 MB per 2s


async def test_all_requests_failed(patch_run_one_test: FakeRunOneTest):
    patch_run_one_test([RequestResult(success=False, error="error")] * 2)

    resp = await ms.measure_speed(SpeedTestRequest(url=URL, tries=2))

    assert resp.success_results == []
    assert resp.avg_request_time_ms == 0
    assert resp.speed_mb_per_s == 0


async def test_zero_elapsed_time_does_not_divide_by_zero(patch_run_one_test: FakeRunOneTest):
    patch_run_one_test([RequestResult(success=True, bytes_downloaded=MIB, elapsed_ms=0)])

    resp = await ms.measure_speed(SpeedTestRequest(url=URL, tries=1))

    assert resp.speed_mb_per_s == 0.0


async def test_makes_exactly_tries_requests_to_given_url(patch_run_one_test: FakeRunOneTest):
    ok = RequestResult(success=True, bytes_downloaded=1, elapsed_ms=1)
    calls = patch_run_one_test([ok] * 10)

    await ms.measure_speed(SpeedTestRequest(url=URL, tries=10))

    assert calls == [URL] * 10
