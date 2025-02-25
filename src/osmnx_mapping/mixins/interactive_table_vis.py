from typing import Union, Optional, Dict, List
import geopandas as gpd
import pandas as pd
from IPython.display import display, HTML
from skrub import TableReport
from beartype import beartype


@beartype
class TableVisMixin:
    def interactive_display(
        self,
        dataframe: Union[pd.DataFrame, gpd.GeoDataFrame],
        n_rows: int = 10,
        order_by: Optional[Union[str, List[str]]] = None,
        title: Optional[str] = "Table Report",
        column_filters: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None,
        verbose: int = 1,
    ) -> None:
        if dataframe is not None and 0 < n_rows < len(dataframe):
            report = TableReport(
                dataframe=dataframe,
                n_rows=n_rows,
                order_by=order_by,
                title=title,
                column_filters=column_filters,
                verbose=verbose,
            )
            display(HTML(report.html()))
