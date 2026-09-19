import asyncio
from typing import Annotated

import typer

from speed_tester.dto import SpeedTestRequest
from speed_tester.measure_speed import measure_speed


def main(
        url: Annotated[str, typer.Argument(help="The url to test the speed against")],
        tries: Annotated[int, typer.Option(help="The number of requests to make.")] = 10,
        timeout: Annotated[int, typer.Option(help="Timeout in seconds.")] = 30,
):
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
        raise typer.Exit(1)

    print(f"Average request time: {response.avg_request_time_ms:.2f} ms")
    print(f"Total bytes downloaded: {response.bytes_downloaded}")
    print(f"Speed: {response.speed_mb_per_s:.2f} MB/s")
