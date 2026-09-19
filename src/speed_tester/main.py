import asyncio

from speed_tester.measure_speed import measure_speed
from speed_tester.dto import SpeedTestRequest


def main(url: str, tries: int = 10, timeout: int = 30):
    request = SpeedTestRequest(url=url, tries=tries, timeout=timeout)
    response = asyncio.run(measure_speed(request))
    success_results = response.success_results
    failure_results = response.failure_results

    print("========== Summary ==========")
    print(f"Succeeded: {len(success_results)}")
    print(f"Failed: {len(failure_results)}")

    if failure_results:
        print("Failures:")
        for r in failure_results:
            print(f"  - {r.error}")

    if not success_results:
        print("None of the requests are successful. Try again.")
        return

    print(f"Average request time (ms): {response.avg_request_time_ms:.3f}")
    print(f"Total bytes downloaded: {response.bytes_downloaded}")
    print(f"Speed (Mb/s): {response.speed_mb_per_s:.3f}")
