from collections.abc import Callable

import pytest
from typer.testing import CliRunner, Result

import speed_tester.main as cli
from speed_tester.dto import RequestResult, SpeedTestRequest, SpeedTestResponse

URL = "https://example.test/x.jpg"

EMPTY_RESPONSE = SpeedTestResponse(
    success_results=[], failure_results=[],
    avg_request_time_ms=0, bytes_downloaded=0, speed_mb_per_s=0,
)

type PatchMeasureSpeed = Callable[[SpeedTestResponse], list[SpeedTestRequest]]

runner = CliRunner()


def invoke_app(args: list[str]) -> Result:
    return runner.invoke(cli.app, args)


@pytest.fixture
def patch_measure_speed(monkeypatch: pytest.MonkeyPatch) -> PatchMeasureSpeed:
    """
    Factory: replaces `measure_speed` with a specified response.

    Returns a list of the calls made to `measure_speed`.
    """

    def _patch_measure_speed(response: SpeedTestResponse = EMPTY_RESPONSE) -> list[SpeedTestRequest]:
        calls: list[SpeedTestRequest] = []

        async def fake(request: SpeedTestRequest) -> SpeedTestResponse:
            calls.append(request)
            return response

        monkeypatch.setattr(cli, "measure_speed", fake)

        return calls

    return _patch_measure_speed


def test_prints_summary(patch_measure_speed: PatchMeasureSpeed):
    ok = RequestResult(success=True, bytes_downloaded=1024, elapsed_ms=10)
    patch_measure_speed(SpeedTestResponse(
        success_results=[ok], failure_results=[],
        avg_request_time_ms=12.345, bytes_downloaded=1024, speed_mb_per_s=3.14,
    ))

    result = invoke_app([URL, "--tries", "1"])

    assert result.exit_code == 0
    assert "12.35" in result.output
    assert "1024" in result.output
    assert "3.14" in result.output


def test_prints_failures(patch_measure_speed: PatchMeasureSpeed):
    error_message = "Request failed with status code 404"
    bad = RequestResult(success=False, error=error_message)
    patch_measure_speed(SpeedTestResponse(
        success_results=[], failure_results=[bad],
        avg_request_time_ms=0, bytes_downloaded=0, speed_mb_per_s=0,
    ))

    result = invoke_app([URL, "--tries", "1"])

    assert error_message in result.output


@pytest.mark.parametrize(
    "option, value",
    [
        ("--tries", "0"),
        ("--tries", "-1"),
        ("--timeout", "-0.5")
    ],
)
def test_invalid_option_is_rejected_before_any_request(
        patch_measure_speed: PatchMeasureSpeed, option: str, value: str,
):
    calls = patch_measure_speed(EMPTY_RESPONSE)

    result = invoke_app([URL, option, value])

    assert result.exit_code == 2  # typer code for usage errors
    assert calls == []
