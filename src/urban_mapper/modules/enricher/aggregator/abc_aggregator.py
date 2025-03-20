from abc import ABC, abstractmethod
import pandas as pd
from beartype import beartype
from urban_mapper.utils import require_arguments_not_none


@beartype
class BaseAggregator(ABC):
    @abstractmethod
    def _aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series: ...

    @require_arguments_not_none(
        "input_dataframe", error_msg="No input dataframe provided.", check_empty=True
    )
    def aggregate(self, input_dataframe: pd.DataFrame) -> pd.Series:
        return self._aggregate(input_dataframe)
