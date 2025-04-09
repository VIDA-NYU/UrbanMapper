from beartype import beartype
from .admin_regions_ import AdminRegions


@beartype
class RegionNeighborhoods(AdminRegions):
    def __init__(self) -> None:
        super().__init__()
        self.division_type = "neighborhood"
