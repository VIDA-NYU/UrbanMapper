from beartype import beartype
from .admin_regions_ import AdminRegions


@beartype
class RegionNeighborhoods(AdminRegions):
    """Urban layer implementation for neighbourhood-level administrative regions.

    This class provides methods for loading neighbourhood boundaries from OpenStreetMap.
    It extends the `AdminRegions` base class, specifically targeting neighbourhood-level
    administrative divisions. The class automatically attempts to identify the appropriate
    administrative level for neighbourhoods in different regions, with an option for manual override.

    Neighbourhoods are small, local administrative or cultural divisions typically found within
    cities. They often correspond to OpenStreetMap’s `admin_level` 10, though this can vary by country.
    The class employs heuristics to determine the correct level based on the size and number of divisions
    within a specified area.

    !!! tip "When to Use?"
        Use this class when you need neighbourhood-level administrative boundaries for tasks such as
        urban planning, local governance studies, or providing geographic context for neighbourhood-specific
        datasets.

    Attributes:
        division_type (str): Set to "neighborhood" to instruct the parent class to look for
            neighbourhood-level administrative boundaries.
        layer (GeoDataFrame): The GeoDataFrame containing the neighbourhood boundaries (set after loading).

    Examples:
        Load and visualise neighbourhood boundaries for a city:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> neighborhoods = mapper.urban_layer.region_neighborhoods().from_place("Brooklyn, NY")
        >>> neighborhoods.static_render(
        ...     figsize=(10, 8),
        ...     edgecolor="black",
        ...     alpha=0.7,
        ...     column="name"  # Colour by neighbourhood name if available
        ... )

        Specify a custom administrative level:
        >>> neighborhoods = mapper.urban_layer.region_neighborhoods().from_place(
        ...     "Paris, France",
        ...     overwrite_admin_level="9"  # Use level 9 in Paris instead of the inferred level
        ... )

    !!! note "Administrative Level Inference"
        This class uses heuristics to infer the correct administrative level for neighbourhoods.
        However, as administrative levels vary globally, accuracy is not guaranteed. Use the
        `overwrite_admin_level` parameter in loading methods to manually specify the level if necessary.
    """

    def __init__(self) -> None:
        super().__init__()
        self.division_type = "neighborhood"
