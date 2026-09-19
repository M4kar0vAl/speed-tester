import time

import httpx
from httpx import AsyncClient
from rich.progress import track

from speed_tester.dto import TestResult, SpeedTestRequest, SpeedTestResponse
from speed_tester.utils import elapsed_ms


async def measure_speed(request: SpeedTestRequest) -> SpeedTestResponse:
    timeout_cfg = httpx.Timeout(request.timeout, connect=10.0)
    results = []

    async with AsyncClient(timeout=timeout_cfg, follow_redirects=True) as client:
        for _ in track(range(request.tries), description="Making requests...", transient=True):
            results.append(await run_one_test(client, request.url))

    success_results = [res for res in results if res.success]
    failure_results = [res for res in results if not res.success]

    total_bytes = sum(r.bytes_downloaded for r in success_results)
    total_time_ms = sum(r.elapsed_ms for r in success_results)
    total_time_s = total_time_ms / 1000

    avg_request_time_ms = total_time_ms / len(success_results) if success_results else 0
    speed_mb_per_s = (total_bytes / (1024 * 1024)) / total_time_s if total_time_s != 0 else 0.0

    return SpeedTestResponse(
        success_results=success_results,
        failure_results=failure_results,
        avg_request_time_ms=avg_request_time_ms,
        bytes_downloaded=total_bytes,
        speed_mb_per_s=speed_mb_per_s,
    )


async def run_one_test(client: AsyncClient, url: str) -> TestResult:
    bytes_downloaded = 0
    start = time.perf_counter_ns()

    try:
        async with client.stream("GET", url) as response:
            response.raise_for_status()

            async for chunk in response.aiter_raw():
                bytes_downloaded += len(chunk)

            return TestResult(
                success=True,
                bytes_downloaded=bytes_downloaded,
                elapsed_ms=elapsed_ms(start),
            )
    except httpx.TimeoutException:
        elapsed = elapsed_ms(start)
        return TestResult(
            success=False,
            bytes_downloaded=bytes_downloaded,
            elapsed_ms=elapsed,
            error=f"Timeout after {elapsed:.3f} ms",
        )
    except httpx.HTTPStatusError as e:
        return TestResult(
            success=False,
            error=f"Request failed with status code {e.response.status_code}"
        )
    except httpx.RequestError as e:
        return TestResult(
            success=False,
            error=f"RequestError: {e!r}"
        )
    except Exception as e:
        return TestResult(
            success=False,
            error=f"Unexpected error: {e!r}"
        )
