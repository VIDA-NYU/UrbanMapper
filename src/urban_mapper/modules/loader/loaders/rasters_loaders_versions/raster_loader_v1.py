"""
RasterLoader implementation for UrbanMapper

This Module provides functionality to load raster data (GeoTIFF, JPEG2000, PNG) and convert it into a GeoDataFrame for integration into UrbanMapper.
code 
"""

from pathlib import Path
from typing import Any, Optional, Union, Dict
import geopandas as gpd
import rasterio
import numpy as np
from PIL import Image
from shapely.geometry import Point, Polygon, box
import warnings
from ..abc_loader import LoaderBase
from ...utils.constants import DEFAULT_CRS
from ...utils.decorators import require_attributes


class RasterLoader(LoaderBase):
    """
    Loader for raster data (GeoTIFF, JPEG2000, PNG with world files).

    This loader converts raster data into a GeoDataFrame by creating vector geometries
    from the raster pixels.

    Supported formats:
    - GeoTIFF (.tif, .tiff) - with embedded georeferencing
    - JPEG2000 (.jp2) - with embedded georeferencing  
    - PNG (.png) - with associated world file (.pgw, .pngw, .wld)

    Examples:
        >>> from urban_mapper.modules.loader import RasterLoader
        >>>
        >>> # Basic GeoTIFF loading
        >>> loader = RasterLoader(
        ...     file_path="satellite.tif",
        ...     conversion_strategy="points"
        ... )
        >>> gdf = loader.load_data_from_file()
        >>>
        >>> # PNG with world file and subsampling
        >>> loader = RasterLoader(
        ...     file_path="map.png",
        ...     conversion_strategy="polygons",
        ...     sampling_factor=0.1,
        ...     band_selection=[1]
        ... )
        >>> gdf = loader.load_data_from_file()
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        latitude_column: Optional[str] = None,
        longitude_column: Optional[str] = None,
        coordinate_reference_system: str = DEFAULT_CRS,
        conversion_strategy: str = "points",
        sampling_factor: float = 1.0,
        band_selection: Optional[list] = None,
        nodata_handling: str = "exclude",
        max_pixels: int = 1000000
    ) -> None:
        """
        Initialize the RasterLoader.

        Args:
            file_path: Path to the raster file
            latitude_column: Not used for rasters (kept for compatibility)
            longitude_column: Not used for rasters (kept for compatibility)  
            coordinate_reference_system: Target CRS for the data
            conversion_strategy: Conversion strategy ("points", "polygons", "contours")
            sampling_factor: Sampling factor (0.0-1.0), 1.0 = all pixels
            band_selection: List of bands to process (None = all)
            nodata_handling: NoData value handling ("exclude", "include", "mask")
            max_pixels: Maximum number of pixels to process (memory safety)
        """
        super().__init__(
            file_path=file_path,
            latitude_column=latitude_column,
            longitude_column=longitude_column,
            coordinate_reference_system=coordinate_reference_system,
        )

        # Raster-specific parameters
        self.conversion_strategy = conversion_strategy
        self.sampling_factor = sampling_factor
        self.band_selection = band_selection
        self.nodata_handling = nodata_handling
        self.max_pixels = max_pixels

        # Parameter validation
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """Validate raster-specific parameters."""
        valid_strategies = ["points", "polygons", "contours"]
        if self.conversion_strategy not in valid_strategies:
            raise ValueError(f"conversion_strategy must be one of {valid_strategies}")

        if not 0.0 < self.sampling_factor <= 1.0:
            raise ValueError("sampling_factor must be between 0.0 and 1.0")

        valid_nodata = ["exclude", "include", "mask"]
        if self.nodata_handling not in valid_nodata:
            raise ValueError(f"nodata_handling must be one of {valid_nodata}")

    def _load_data_from_file(self) -> gpd.GeoDataFrame:
        """
        Loads raster data and converts it to a GeoDataFrame.

        Returns:
            GeoDataFrame containing the converted data

        Raises:
            ValueError: If the format is not supported
            FileNotFoundError: If the file does not exist
            RuntimeError: If the conversion fails
        """
        file_ext = self.file_path.suffix.lower()

        try:
            if file_ext in ['.tif', '.tiff']:
                return self._load_geotiff()
            elif file_ext == '.jp2':
                return self._load_jpeg2000()
            elif file_ext == '.png':
                return self._load_png_with_worldfile()
            else:
                raise ValueError(f"Unsupported raster format: {file_ext}")

        except Exception as e:
            raise RuntimeError(f"Failed to load raster data: {str(e)}") from e

    def _load_geotiff(self) -> gpd.GeoDataFrame:
        """Load a GeoTIFF file."""
        with rasterio.open(self.file_path) as src:
            return self._process_rasterio_dataset(src)

    def _load_jpeg2000(self) -> gpd.GeoDataFrame:
        """Load a JPEG2000 file.""" 
        with rasterio.open(self.file_path) as src:
            return self._process_rasterio_dataset(src)

    def _load_png_with_worldfile(self) -> gpd.GeoDataFrame:
        """Load a PNG with its world file."""
        # Search for the world file
        world_file = self._find_world_file()
        if world_file is None:
            raise FileNotFoundError(f"No world file found for {self.file_path}")

        # Read the world file
        transform = self._parse_world_file(world_file)

        # Read the PNG
        img = Image.open(self.file_path)
        array = np.array(img)

        # Create a virtual rasterio dataset
        from rasterio.transform import Affine

        # Convert to rasterio dataset for uniform processing
        profile = {
            'driver': 'MEM',
            'height': array.shape[0],
            'width': array.shape[1], 
            'count': len(array.shape) if len(array.shape) == 3 else 1,
            'dtype': array.dtype,
            'transform': transform,
            'crs': self.coordinate_reference_system
        }

        with rasterio.io.MemoryFile() as memfile:
            with memfile.open(**profile) as dataset:
                if len(array.shape) == 3:
                    for i in range(array.shape[2]):
                        dataset.write(array[:, :, i], i + 1)
                else:
                    dataset.write(array, 1)

                return self._process_rasterio_dataset(dataset)

    def _find_world_file(self) -> Optional[Path]:
        """Search for the world file associated with the PNG."""
        base_path = self.file_path.with_suffix('')

        # Possible extensions for PNG world files
        world_extensions = ['.pgw', '.pngw', '.wld']

        for ext in world_extensions:
            world_path = base_path.with_suffix(ext)
            if world_path.exists():
                return world_path

        return None

    def _parse_world_file(self, world_file: Path) -> 'rasterio.transform.Affine':
        """Parse a world file and return the affine transformation."""
        try:
            with open(world_file, 'r') as f:
                lines = [float(line.strip()) for line in f.readlines()]

            if len(lines) != 6:
                raise ValueError("World file must contain exactly 6 lines")

            # World file format: A, D, B, E, C, F
            # Where A,E = pixel size, B,D = rotation, C,F = origin coordinates
            from rasterio.transform import Affine
            return Affine(lines[0], lines[2], lines[4], lines[1], lines[3], lines[5])

        except Exception as e:
            raise ValueError(f"Failed to parse world file {world_file}: {str(e)}") from e

    def _process_rasterio_dataset(self, src) -> gpd.GeoDataFrame:
        """Process a rasterio dataset and convert it to a GeoDataFrame."""
        # Size validation
        total_pixels = src.height * src.width
        if total_pixels > self.max_pixels:
            suggested_factor = self.max_pixels / total_pixels
            warnings.warn(
                f"Dataset has {total_pixels} pixels, exceeding limit of {self.max_pixels}. "
                f"Consider setting sampling_factor to {suggested_factor:.3f} or less."
            )

        # Band selection
        bands_to_read = self.band_selection or list(range(1, src.count + 1))

        # Read data with sampling
        if self.sampling_factor < 1.0:
            return self._read_sampled_data(src, bands_to_read)
        else:
            return self._read_full_data(src, bands_to_read)

    def _read_sampled_data(self, src, bands_to_read: list) -> gpd.GeoDataFrame:
        """Read data with spatial sampling."""
        # Compute the sampling grid
        step = int(1.0 / self.sampling_factor)

        rows = list(range(0, src.height, step))
        cols = list(range(0, src.width, step))

        return self._extract_geometries_from_coords(src, rows, cols, bands_to_read)

    def _read_full_data(self, src, bands_to_read: list) -> gpd.GeoDataFrame:
        """Read all raster data."""
        rows = list(range(src.height))
        cols = list(range(src.width))

        return self._extract_geometries_from_coords(src, rows, cols, bands_to_read)

    def _extract_geometries_from_coords(
        self, 
        src, 
        rows: list, 
        cols: list, 
        bands_to_read: list
    ) -> gpd.GeoDataFrame:
        """Extract geometries according to the chosen strategy."""
        if self.conversion_strategy == "points":
            return self._create_point_geometries(src, rows, cols, bands_to_read)
        elif self.conversion_strategy == "polygons":
            return self._create_polygon_geometries(src, rows, cols, bands_to_read)
        elif self.conversion_strategy == "contours":
            return self._create_contour_geometries(src, bands_to_read)
        else:
            raise ValueError(f"Unknown conversion strategy: {self.conversion_strategy}")

    def _create_point_geometries(
        self, 
        src, 
        rows: list, 
        cols: list, 
        bands_to_read: list
    ) -> gpd.GeoDataFrame:
        """Create Point geometries for each pixel."""
        geometries = []
        data_rows = []

        for row in rows:
            for col in cols:
                # Coordinates of the pixel center
                lon, lat = src.transform * (col + 0.5, row + 0.5)

                # Read values for all bands
                pixel_values = {}
                skip_pixel = False

                for band_idx in bands_to_read:
                    try:
                        window = rasterio.windows.Window(col, row, 1, 1)
                        value = src.read(band_idx, window=window)[0, 0]

                        # NoData handling
                        if src.nodatavals and src.nodatavals[band_idx - 1] is not None:
                            if value == src.nodatavals[band_idx - 1]:
                                if self.nodata_handling == "exclude":
                                    skip_pixel = True
                                    break
                                elif self.nodata_handling == "mask":
                                    value = np.nan

                        pixel_values[f'band_{band_idx}'] = value

                    except IndexError:
                        skip_pixel = True
                        break

                if not skip_pixel:
                    geometries.append(Point(lon, lat))
                    pixel_values.update({
                        'row': row,
                        'col': col,
                        'x': lon,
                        'y': lat
                    })
                    data_rows.append(pixel_values)

        # Create the GeoDataFrame
        if not geometries:
            # Return an empty GeoDataFrame with the appropriate structure
            columns = [f'band_{i}' for i in bands_to_read] + ['row', 'col', 'x', 'y']
            gdf = gpd.GeoDataFrame(columns=columns + ['geometry'])
            gdf = gdf.set_crs(src.crs or self.coordinate_reference_system)
        else:
            gdf = gpd.GeoDataFrame(data_rows, geometry=geometries)
            gdf = gdf.set_crs(src.crs or self.coordinate_reference_system)

        # CRS conversion if needed
        if gdf.crs != self.coordinate_reference_system:
            gdf = gdf.to_crs(self.coordinate_reference_system)

        return gdf

    def _create_polygon_geometries(
        self, 
        src, 
        rows: list, 
        cols: list, 
        bands_to_read: list
    ) -> gpd.GeoDataFrame:
        """Create Polygon geometries for each pixel."""
        geometries = []
        data_rows = []

        for row in rows:
            for col in cols:
                # Coordinates of the pixel corners
                left, top = src.transform * (col, row)
                right, bottom = src.transform * (col + 1, row + 1)

                # Read values for all bands
                pixel_values = {}
                skip_pixel = False

                for band_idx in bands_to_read:
                    try:
                        window = rasterio.windows.Window(col, row, 1, 1)
                        value = src.read(band_idx, window=window)[0, 0]

                        # NoData handling
                        if src.nodatavals and src.nodatavals[band_idx - 1] is not None:
                            if value == src.nodatavals[band_idx - 1]:
                                if self.nodata_handling == "exclude":
                                    skip_pixel = True
                                    break
                                elif self.nodata_handling == "mask":
                                    value = np.nan

                        pixel_values[f'band_{band_idx}'] = value

                    except IndexError:
                        skip_pixel = True
                        break

                if not skip_pixel:
                    # Create the polygon for the pixel
                    pixel_polygon = box(left, bottom, right, top)
                    geometries.append(pixel_polygon)

                    center_lon, center_lat = src.transform * (col + 0.5, row + 0.5)
                    pixel_values.update({
                        'row': row,
                        'col': col,
                        'center_x': center_lon,
                        'center_y': center_lat
                    })
                    data_rows.append(pixel_values)

        # Create the GeoDataFrame
        if not geometries:
            columns = [f'band_{i}' for i in bands_to_read] + ['row', 'col', 'center_x', 'center_y']
            gdf = gpd.GeoDataFrame(columns=columns + ['geometry'])
            gdf = gdf.set_crs(src.crs or self.coordinate_reference_system)
        else:
            gdf = gpd.GeoDataFrame(data_rows, geometry=geometries)
            gdf = gdf.set_crs(src.crs or self.coordinate_reference_system)

        # CRS conversion if needed
        if gdf.crs != self.coordinate_reference_system:
            gdf = gdf.to_crs(self.coordinate_reference_system)

        return gdf

    def _create_contour_geometries(self, src, bands_to_read: list) -> gpd.GeoDataFrame:
        """Create contour geometries (iso-value lines)."""
        # This implementation would require scikit-image or matplotlib
        raise NotImplementedError(
            "Contour extraction not yet implemented. "
            "Use 'points' or 'polygons' conversion strategy."
        )

    def preview(self, format: str = "ascii") -> Any:
        """
        Generate a preview of this raster loader.

        Args:
            format: Output format ("ascii" or "json")

        Returns:
            Representation of the loader in the requested format

        Raises:
            ValueError: If the format is not supported
        """
        # Collect raster metadata
        try:
            if self.file_path.suffix.lower() == '.png':
                # For PNG, basic info + world file
                img = Image.open(self.file_path)
                width, height = img.size
                bands = len(img.getbands()) if hasattr(img, 'getbands') else 1
                world_file = self._find_world_file()

                metadata = {
                    'width': width,
                    'height': height,
                    'bands': bands,
                    'world_file': str(world_file) if world_file else "Not found",
                    'total_pixels': width * height
                }
            else:
                # For GeoTIFF/JPEG2000, full metadata via rasterio
                with rasterio.open(self.file_path) as src:
                    metadata = {
                        'width': src.width,
                        'height': src.height,
                        'bands': src.count,
                        'dtype': str(src.dtypes[0]) if src.dtypes else 'unknown',
                        'crs': str(src.crs) if src.crs else 'undefined',
                        'bounds': src.bounds,
                        'transform': str(src.transform),
                        'total_pixels': src.width * src.height
                    }
        except Exception as e:
            metadata = {'error': f"Could not read raster metadata: {str(e)}"}

        if format == "ascii":
            lines = [
                f"Loader: RasterLoader",
                f" File: {self.file_path}",
                f" Format: {self.file_path.suffix.upper()}",
                f" Conversion Strategy: {self.conversion_strategy}",
                f" Sampling Factor: {self.sampling_factor}",
                f" Target CRS: {self.coordinate_reference_system}",
                ""
            ]

            for key, value in metadata.items():
                lines.append(f" {key.replace('_', ' ').title()}: {value}")

            return "\n".join(lines)

        elif format == "json":
            return {
                "loader": "RasterLoader",
                "file": str(self.file_path),
                "format": self.file_path.suffix.upper(),
                "conversion_strategy": self.conversion_strategy,
                "sampling_factor": self.sampling_factor,
                "target_crs": self.coordinate_reference_system,
                "metadata": metadata
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
            raise ValueError(f"Unsupported format: {format}")
