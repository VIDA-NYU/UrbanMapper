
from ..abc_loader import LoaderBase

class RasterLoader(LoaderBase):
    

    def __init__(self, file_path, latitude_column=None, longitude_column=None, coordinate_reference_system=None, **kwargs):
        
        super().__init__(file_path)
    
    def set_raster_strategy(self, strategy):
        
        self.raster_strategy = strategy

    def set_sampling_factor(self, sampling_factor):
        
        self.sampling_factor = sampling_factor

    def set_band_selection(self, bands):
        
        self.band_selection = bands

    def set_nodata_handling(self, nodata_handling):
        
        self.nodata_handling = nodata_handling

    def set_max_pixels(self, max_pixels):
       
        self.max_pixels = max_pixels


    def _load_data_from_file(self):
        
        import os
        import rasterio
        from PIL import Image
        import numpy as np

        ext = os.path.splitext(self.file_path)[1].lower()

        if ext in ['.tif', '.tiff']:  # GeoTIFF 
            try:
                with rasterio.open(self.file_path) as src:
                    data = src.read(1)  # read the first band
                    profile = src.profile
                # return a dictionary with standard keys
                return {
                    'data_shape': data.shape,
                    'data_dtype': data.dtype.name,
                    'crs': str(profile['crs']),
                    'transform': str(profile['transform'])
                }
            except Exception as e:
                raise RuntimeError(f"Error in the loading of the raster {e}")
            
        elif ext == ".png": # Load PNG with world file
            return self._load_png_with_worldfile()

        else:
            raise RuntimeError(f"Unsupported raster format: {ext}")
    
    def _load_png_with_worldfile(self):
        
        from PIL import Image
        import numpy as np
        import os

        # Open the PNG image
        img = Image.open(self.file_path)
        data = np.array(img)

        # Search for the associated world file
        base, _ = os.path.splitext(self.file_path)
        worldfile_extensions = [".pgw", ".wld", ".pngw"]
        worldfile_path = None
        for ext in worldfile_extensions:
            candidate = base + ext
            if os.path.exists(candidate):
                worldfile_path = candidate
                break
        if not worldfile_path:
            raise FileNotFoundError(f"No world file found for {self.file_path}")

        # Read the 6 parameters from the world file
        with open(worldfile_path, "r") as f:
            params = [float(line.strip()) for line in f.readlines()]
        if len(params) != 6:
            raise ValueError("World file must contain 6 lines.")

        # Return a summary
        return {
            "data_shape": data.shape,
            "data_dtype": str(data.dtype),
            "transform": params,
            "crs": None  # A PNG + world file does not always have an explicit CRS
        }


    def preview(self, n=5):
       
        raise NotImplementedError("Raster preview is not yet implemented.")

