from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Type(Enum):
    BULL = 1
    BEAR = -1


class Status(Enum):
    SUCCESS = 3
    FAIL = 4


EVALUATION_THRESHOLD = 5
EVALUATION_DIFF_RATE = 1.0013


@dataclass
class BenchmarkData:
    time: datetime
    suggestion_type: Type
    trigger_close: float
    counter: int
    status: Status


class Benchmark:
    def __init__(self) -> None:
        self._data: dict[datetime, BenchmarkData] = {}
        self.dataToDelete: list[datetime] = []
        self._totalSuggestion: int = 0
        self._success: int = 0
        self._fail: int = 0

    def create(self, time: datetime, suggestion_type: Type, trigger_close: float) -> None:
        self._data[time] = BenchmarkData(time, suggestion_type, trigger_close, 0, Status.FAIL)
        self._totalSuggestion += 1
        print(f"Creating benchmark for suggestion {time}")

    def update(self, new_close: float) -> None:
        self.dataToDelete.clear()
        for v in self._data.values():
            if v.counter > EVALUATION_THRESHOLD:
                v.status = Status.FAIL
                self.record_result(v)
            elif (
                (new_close / v.trigger_close) > EVALUATION_DIFF_RATE
                and v.suggestion_type == Type.BULL
                or (v.trigger_close / new_close) > EVALUATION_DIFF_RATE
                and v.suggestion_type == Type.BEAR
            ):
                v.status = Status.SUCCESS
                self.record_result(v)
            else:
                v.counter += 1

        for k in self.dataToDelete:
            del self._data[k]

    def record_result(self, benchmark_data: BenchmarkData) -> None:
        print(f"Benchmark time: {benchmark_data.time} status: {benchmark_data.status}")
        self.dataToDelete.append(benchmark_data.time)
        if benchmark_data.status == Status.SUCCESS:
            self._success += 1
        elif benchmark_data.status == Status.FAIL:
            self._fail += 1
        print(
            f"Total suggestion: {self._totalSuggestion}, success: {self._success}, fail: {self._fail}"  # noqa: COM812
        )
        print(
            f"Success rate: {self._success / self._totalSuggestion}, fail rate: {self._fail / self._totalSuggestion}"  # noqa: COM812
        )
