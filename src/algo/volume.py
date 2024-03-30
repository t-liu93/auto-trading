import pandas as pd
from algo.algo import Algo


class Volume(Algo):
    def __init__(self) -> None:
        super().__init__()
        self._volumes: pd.DataFrame = {}
