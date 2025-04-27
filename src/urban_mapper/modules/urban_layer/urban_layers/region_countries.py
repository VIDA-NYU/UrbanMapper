from beartype import beartype
from .admin_regions_ import AdminRegions


@beartype
class RegionCountries(AdminRegions):
    """Urban layer implementation for country-level administrative regions.

    This class provides methods for loading country boundaries from OpenStreetMap.
    It extends the `AdminRegions` base class, specifically targeting country-level
    administrative divisions. The class automatically attempts to identify the appropriate
    administrative level for countries in different contexts, with an option for manual override.

    Countries represent the highest level of administrative divisions in most global datasets.
    They typically correspond to OpenStreetMap’s `admin_level` 2, though variations exist in
    some special cases. The class uses heuristics to determine the correct level based on the
    size and connectivity of boundaries within a specified area.

    !!! tip "When to Use?"
        Use this class when you need country-level administrative boundaries for tasks such as
        global analysis, international comparisons, or providing geographic context for country-specific
        datasets.

    Attributes:
        division_type (str): Set to "country" to instruct the parent class to look for
            country-level administrative boundaries.
        layer (GeoDataFrame): The GeoDataFrame containing the country boundaries (set after loading).

    Examples:
        Load and visualise country boundaries for a continent:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> countries = mapper.urban_layer.region_countries().from_place("Europe")
        >>> countries.static_render(
        ...     figsize=(15, 10),
        ...     edgecolor="black",
        ...     alpha=0.6,
        ...     column="name"  # Colour by country name
        ... )

        Specify a custom administrative level:
        >>> countries = mapper.urban_layer.region_countries().from_place(
        ...     "World",
        ...     overwrite_admin_level="2"  # Explicitly use level 2 for countries
        ... )

    !!! note "Administrative Level Inference"
        This class uses heuristics to infer the correct administrative level for countries.
        However, as administrative levels can vary, accuracy is not guaranteed. Use the
        `overwrite_admin_level` parameter in loading methods to manually specify the level
        if necessary.
    """

    def __init__(self) -> None:
        super().__init__()
        self.division_type = "country"
