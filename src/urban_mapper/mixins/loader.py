from urban_mapper.modules.loader.loader_factory import LoaderFactory


class LoaderMixin(LoaderFactory):
    """
    Mixin providing access to data loading functionality through the UrbanMapper interface.

    This class extends LoaderFactory to provide a seamless integration point for
    data loading capabilities within the UrbanMapper ecosystem. It enables users
    to load data from various formats including CSV, Shapefile, and Parquet files
    through a fluent interface.

    The mixin pattern allows UrbanMapper to compose functionality from multiple
    specialized components while maintaining a clean, unified API.

    Inherits all methods from LoaderFactory, including:
        - from_csv(): Load data from CSV files
        - from_shapefile(): Load data from Shapefiles  
        - from_parquet(): Load data from Parquet files
        - with_coordinate_reference_system(): Set CRS for loaded data

    Example:
        >>> mapper = UrbanMapper()
        >>> # Access loader through the mixin
        >>> data = mapper.loader.from_csv('restaurants.csv')
        >>> # Chain operations using fluent interface
        >>> data = mapper.loader.from_csv('data.csv').with_coordinate_reference_system('EPSG:3857')

    See Also:
        LoaderFactory: The underlying factory class providing loader implementations
        LoaderBase: Abstract base class for all loaders
    """

    def __init__(self):
        super().__init__()
