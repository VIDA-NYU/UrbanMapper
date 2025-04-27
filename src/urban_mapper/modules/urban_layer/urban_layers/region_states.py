from beartype import beartype
from .admin_regions_ import AdminRegions


@beartype
class RegionStates(AdminRegions):
    """Urban layer implementation for state and province-level administrative regions.

    This class provides methods for loading state and province boundaries from OpenStreetMap.
    It extends the `AdminRegions` base class, specifically targeting state-level administrative
    divisions. The class automatically attempts to identify the appropriate administrative
    level for states or provinces in different regions, with an option for manual override.

    States and provinces are mid-level administrative units, typically found within countries.
    They often correspond to OpenStreetMap’s `admin_level` 4, though this can vary by country.
    The class employs heuristics to determine the correct level based on the size and number
    of divisions within a specified area.

    !!! tip "When to Use?"
        Use this class when you need state or province-level administrative boundaries for
        tasks such as regional analysis, governance studies, or providing geographic context
        for state-specific datasets.

    Attributes:
        division_type (str): Set to "state" to instruct the parent class to look for
            state-level administrative boundaries.
        layer (GeoDataFrame): The GeoDataFrame containing the state boundaries (set after loading).

    Examples:
        Load and visualise state boundaries for a country:
        >>> from urban_mapper import UrbanMapper
        >>> mapper = UrbanMapper()
        >>> states = mapper.urban_layer.region_states().from_place("United States")
        >>> states.static_render(
        ...     figsize=(12, 8),
        ...     edgecolor="black",
        ...     alpha=0.5,
        ...     column="name"  # Colour by state name
        ... )

        Specify a custom administrative level:
        >>> states = mapper.urban_layer.region_states().from_place(
        ...     "Canada",
        ...     overwrite_admin_level="4"  # Explicitly use level 4 for Canadian provinces
        ... )

    !!! note "Administrative Level Inference"
        This class uses heuristics to infer the correct administrative level for states.
        However, as administrative levels vary globally, accuracy is not guaranteed. Use the
        `overwrite_admin_level` parameter in loading methods to manually specify the level
        if necessary.
    """

    def __init__(self) -> None:
        super().__init__()
        self.division_type = "state"
