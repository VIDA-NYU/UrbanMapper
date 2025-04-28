from typing import Union, Optional, Dict, List
import geopandas as gpd
import pandas as pd
from IPython.display import display, HTML
from skrub import TableReport
from beartype import beartype


@beartype
class TableVisMixin:
    """Mixin for creating interactive data table visualisations in notebooks.

    This mixin provides methods for displaying dataframes as interactive tables
    with filtering and sorting capabilities. It enhances the data exploration
    experience in Jupyter notebooks by offering richer visualisations compared
    to standard DataFrame displays.

    All this thanks to Skrub's `TableReport` class. Find out more about [Skrub, via their official doc](https://skrub-data.org/stable/).

    Examples:
        >>> from urban_mapper import UrbanMapper
        >>> import geopandas as gpd
        >>>
        >>> # Initialise UrbanMapper
        >>> mapper = UrbanMapper()
        >>>
        >>> # Load sample data
        >>> data = gpd.read_file("nyc_taxi_trips.geojson")
        >>>
        >>> # Display as an interactive table
        >>> mapper.table_vis.interactive_display(
        ...     dataframe=data,
        ...     n_rows=15,
        ...     order_by="trip_distance",
        ...     title="NYC Taxi Trips"
        ... )
    """

    def interactive_display(
        self,
        dataframe: Union[pd.DataFrame, gpd.GeoDataFrame],
        n_rows: int = 10,
        order_by: Optional[Union[str, List[str]]] = None,
        title: Optional[str] = "Table Report",
        column_filters: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None,
        verbose: int = 1,
    ) -> None:
        """Display a `dataframe` as an `interactive HTML` table with sorting and filtering capabilities.

        This method generates an enhanced table visualisation, enabling users to
        explore data more effectively than with standard DataFrame displays. It
        supports sorting by columns, applying filters, and customising the number
        of rows displayed.

        Find out more about the `TableReport` class in the [Skrub documentation](https://skrub-data.org/stable/reference/generated/skrub.TableReport.html#skrub.TableReport).

        Args:
            dataframe (Union[pd.DataFrame, gpd.GeoDataFrame]): The dataframe to display.
            n_rows (int, optional): Number of rows to show in the table. Defaults to 10.
            order_by (Optional[Union[str, List[str]]], optional): Column(s) to sort the data by. Defaults to None.
            title (Optional[str], optional): Title to display above the table. Defaults to "Table Report".
            column_filters (Optional[Dict[str, Dict[str, Union[str, List[str]]]]], optional): Filters to apply to specific columns.
                Format: {column_name: {filter_type: filter_value}}, e.g., {"fare_amount": {"greater_than": 50.0}}. Defaults to None.
            verbose (int, optional): Verbosity level for report generation. Defaults to 1.

        Returns:
            None: Displays the table directly in the notebook.

        Examples:
            >>> # Basic display with default settings
            >>> mapper.table_vis.interactive_display(dataframe=data)
            >>>
            >>> # Advanced display with sorting and filtering
            >>> mapper.table_vis.interactive_display(
            ...     dataframe=taxi_data,
            ...     n_rows=20,
            ...     order_by=["trip_distance", "fare_amount"],
            ...     title="High-Value Taxi Trips",
            ...     column_filters={
            ...         "payment_type": {"equals": "credit card"},
            ...         "fare_amount": {"greater_than": 50.0}
            ...     },
            ...     verbose=2
            ... )
        """
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
