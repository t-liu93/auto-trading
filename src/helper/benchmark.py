from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from algo.ma import Ma


class Type(Enum):
    BULL = 1
    BEAR = -1


class Status(Enum):
    PARTIAL_SUCCESS = 2
    SUCCESS = 3
    FAIL = 4


FAST_MID_CANDLE_THRESHOLD = 2
FAST_SLOW_CANDLE_THRESHOLD = 3
MID_SLOW_CANDLE_THRESHOLD = 4


@dataclass
class BenchmarkData:
    time: datetime
    suggestion_type: Type
    fast_mid_counter: int
    fast_slow_counter: int
    mid_slow_counter: int
    status: Status


class Benchmark:
    def __init__(self) -> None:
        self._data: dict[datetime, BenchmarkData] = {}
        self.dataToDelete: list[datetime] = []
        self._totalSuggestion: int = 0
        self._partialSuccess: int = 0
        self._success: int = 0
        self._fail: int = 0

    def create(self, time: datetime, suggestion_type: Type) -> None:
        self._data[time] = BenchmarkData(time, suggestion_type, 0, 0, 0, Status.FAIL)
        self._totalSuggestion += 1
        print(f"Creating benchmark for suggestion {time}")

    def update(self, ma: Ma) -> None:  # noqa: C901, PLR0912
        self.dataToDelete.clear()
        for v in self._data.values():
            if (
                v.fast_mid_counter > FAST_MID_CANDLE_THRESHOLD
                or v.fast_slow_counter > FAST_SLOW_CANDLE_THRESHOLD
                or v.mid_slow_counter > MID_SLOW_CANDLE_THRESHOLD
            ):
                self.record_result(v)
                continue
            counter = 0
            if v.suggestion_type == Type.BULL:
                if ma.ma.iloc[-1]["ma_fast"] > ma.ma.iloc[-1]["ma_mid"]:
                    counter += 1
                else:
                    v.fast_mid_counter += 1
                if ma.ma.iloc[-1]["ma_fast"] > ma.ma.iloc[-1]["ma_slow"]:
                    counter += 1
                else:
                    v.fast_slow_counter += 1
                if ma.ma.iloc[-1]["ma_mid"] > ma.ma.iloc[-1]["ma_slow"]:
                    counter += 1
                else:
                    v.mid_slow_counter += 1
            else:
                if ma.ma.iloc[-1]["ma_fast"] < ma.ma.iloc[-1]["ma_mid"]:
                    counter += 1
                else:
                    v.fast_mid_counter += 1
                if ma.ma.iloc[-1]["ma_fast"] < ma.ma.iloc[-1]["ma_slow"]:
                    counter += 1
                else:
                    v.fast_slow_counter += 1
                if ma.ma.iloc[-1]["ma_mid"] < ma.ma.iloc[-1]["ma_slow"]:
                    counter += 1
                else:
                    v.mid_slow_counter += 1
            if counter > 0 and counter < 3:  # noqa: PLR2004
                v.status = Status.PARTIAL_SUCCESS
            elif counter == 3:  # noqa: PLR2004
                v.status = Status.SUCCESS
                self.record_result(v)
        for k in self.dataToDelete:
            del self._data[k]

    def record_result(self, benchmark_data: BenchmarkData) -> None:
        print(f"Benchmark time: {benchmark_data.time} status: {benchmark_data.status}")
        self.dataToDelete.append(benchmark_data.time)
        if benchmark_data.status == Status.SUCCESS:
            self._success += 1
        elif benchmark_data.status == Status.PARTIAL_SUCCESS:
            self._partialSuccess += 1
        elif benchmark_data.status == Status.FAIL:
            self._fail += 1
        print(
            f"Total suggestion: {self._totalSuggestion}, success: {self._success}, partial success: {self._partialSuccess}, fail: {self._fail}"  # noqa: COM812
        )
        print(
            f"Success rate: {self._success / self._totalSuggestion}, partial success rate: {self._partialSuccess / self._totalSuggestion}, fail rate: {self._fail / self._totalSuggestion}"  # noqa: COM812, E501
        )
