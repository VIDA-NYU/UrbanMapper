from abc import ABC, abstractmethod
import pandas as pd
from beartype import beartype
from osmnx_mapping.utils import require_arguments_not_none


class BaseAggregator(ABC):
    @abstractmethod
    @beartype
    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series: ...

    @beartype
    @require_arguments_not_none(
        "input_dataframe", error_msg="No input dataframe provided.", check_empty=True
    )
    def aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series:
        return self._aggregate(input_dataframe)
