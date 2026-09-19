from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestResult:
    success: bool
    bytes_downloaded: int = 0
    elapsed_ms: float = 0.0
    error: str | None = None


@dataclass(frozen=True, slots=True)
class SpeedTestRequest:
    url: str
    tries: int = 10
    timeout: int = 30


@dataclass(frozen=True, slots=True)
class SpeedTestResponse:
    success_results: list[TestResult]
    failure_results: list[TestResult]
    avg_request_time_ms: float
    bytes_downloaded: int
    speed_mb_per_s: float
