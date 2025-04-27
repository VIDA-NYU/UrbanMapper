from beartype import beartype
from .admin_regions_ import AdminRegions


@beartype
class RegionCities(AdminRegions):
    """Urban layer implementation for city-level administrative regions.

    This class facilitates the loading of city and municipal boundaries from OpenStreetMap,
    extending the `AdminRegions` base class to target city-level administrative divisions.
    It employs heuristics to automatically determine the appropriate administrative level
    for cities across different regions, with an option for manual override.

    Cities and municipalities represent medium-sized administrative units, typically under
    local government jurisdiction. While they often correspond to OpenStreetMap’s
    `admin_level` 8, variations across countries are common. This class adapts to such
    differences by analysing the size and number of divisions within a specified area.

    !!! tip "When to Use?"
        Employ this class when you need city-level administrative boundaries for tasks like
        urban analysis, municipal planning, population studies, or providing geographic
        context for city-specific datasets.

    Attributes:
        division_type (str): Fixed to "city", directing the parent class to target city-level
            administrative boundaries.
        layer (GeoDataFrame): Holds the city boundaries as a `GeoDataFrame`, populated after
            loading via methods like `from_place`.

    Examples:
        Load and visualise city boundaries for a region:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> cities = mapper.urban_layer.region_cities().from_place("Greater Manchester, England")
        >>> cities.static_render(
        ...     figsize=(12, 10),
        ...     edgecolor="black",
        ...     alpha=0.5,
        ...     column="name"  # Colour by city name if available
        ... )

        Specify a custom administrative level:
        >>> cities = mapper.urban_layer.region_cities().from_place(
        ...     "Bavaria, Germany",
        ...     overwrite_admin_level="6"  # Override inferred level with 6
        ... )

    !!! note "Administrative Level Inference"
        This class attempts to infer the correct administrative level for cities using
        heuristics. However, as levels differ globally, accuracy isn’t guaranteed. Use the
        `overwrite_admin_level` parameter in loading methods to manually set the level if
        needed.
    """

    def __init__(self) -> None:
        super().__init__()
        self.division_type = "city"
