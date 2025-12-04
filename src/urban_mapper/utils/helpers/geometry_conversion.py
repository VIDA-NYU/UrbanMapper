import math, geopandas as gpd, pandas as pd, numpy as np, scipy
from typing import Union, Optional, List, Tuple
from urban_mapper.config import DEFAULT_CRS

from shapely.ops import polygonize
from shapely import (
    Point,
    LineString,
    Polygon,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
)
from shapely.geometry import shape, mapping, box
from shapely.geometry.base import BaseGeometry

from rasterio import features, mask, DatasetReader
from rasterio.transform import from_bounds
from rasterio.enums import MergeAlg
from affine import Affine

from sklearn.cluster import KMeans


def extract_points(geom: BaseGeometry) -> List[BaseGeometry]:
    """Extract a list of Points from a geometry

    Args:
        geom: GeoDataframe geometry

    Returns:
        List o Points
    """
    if isinstance(geom, (Polygon, LineString)):
        coords = geom.exterior.coords if isinstance(geom, Polygon) else geom.coords
        return [Point(p) for p in coords]
    elif isinstance(geom, (MultiPolygon, MultiLineString)):
        return [
            Point(p)
            for g in geom.geoms
            for p in (g.exterior.coords if isinstance(g, Polygon) else g.coords)
        ]
    elif isinstance(geom, MultiPoint):
        return list(geom.geoms)
    elif isinstance(geom, Point):
        return [geom]

    return []


def extract_lines(geom: BaseGeometry) -> List[BaseGeometry]:
    """Extract a list of Lines from a geometry

    Args:
        geom: GeoDataframe geometry

    Returns:
        List o Points
    """
    if isinstance(geom, Polygon):
        return [geom.exterior]
    elif isinstance(geom, MultiPolygon):
        return [poly.exterior for poly in geom.geoms]
    elif isinstance(geom, MultiPoint):
        return [LineString(geom.geoms)]
    elif isinstance(geom, MultiLineString):
        return list(geom.geoms)

    return []


def to_point(input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Converts a GeoDataframe with any geometry object into a GeoDataframe of Point geometry.
       It keeps the original geometry column and adds a new one with Points that is set as active_geometry_name

    Args:
        input_geodataframe: GeoDataframe to be converted

    Returns:
        A GeoDataframe onlye with Point geometry
    """
    new_data = []
    col_name = input_geodataframe.active_geometry_name
    new_col = col_name + "2point"

    col_list = list(input_geodataframe.columns) + [new_col]
    first_geometry = input_geodataframe.iloc[0][col_name]

    # A naive way to identify if the dataset already contains points
    # TODO: some datasets have a heterogeneous geometry with Points, Lines, etc. Find a way to better test it.
    if isinstance(first_geometry, Point):
        return input_geodataframe

    for _, row in input_geodataframe.iterrows():
        geom = row[col_name]

        for point in extract_points(geom):
            new = gpd.GeoSeries([point], index=[new_col])
            new_data.append(pd.concat([row, new]))

    new_data = gpd.GeoDataFrame(new_data, columns=col_list, geometry=col_name)
    new_data = new_data.set_geometry(new_col)
    new_data = new_data.set_crs(input_geodataframe.crs)

    return new_data


def to_line(input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Converts a GeoDataframe with any geometry object into a GeoDataframe of LineString geometry
       It keeps the original geometry column and adds a new one with LineString that is set as active_geometry_name

    Args:
        input_geodataframe: GeoDataframe to be converted

    Returns:
        A GeoDataframe onlye with LineString geometry
    """
    new_data = []
    col_name = input_geodataframe.active_geometry_name
    new_col = col_name + "2line"

    col_list = list(input_geodataframe.columns) + [new_col]

    first_geometry = input_geodataframe.iloc[0][col_name]

    # A naive way to identify if the dataset already contains lines
    # TODO: some datasets have a heterogeneous geometry with Points, Lines, etc. Find a way to better test it.
    if isinstance(first_geometry, LineString):
        return input_geodataframe

    # Special case: points grouped into lines
    if isinstance(first_geometry, Point):
        # Group by non-geometry columns
        non_geom_cols = [
            col
            for col in input_geodataframe.columns
            if not isinstance(input_geodataframe[col], gpd.GeoSeries)
        ]

        grouped = input_geodataframe.groupby(non_geom_cols)[col_name].apply(
            lambda x: LineString(x.tolist())
        )

        new_data = gpd.GeoDataFrame(grouped.reset_index())
        new_data.columns = non_geom_cols + [new_col]
    else:
        for _, row in input_geodataframe.iterrows():
            geom = row[col_name]

            for line in extract_lines(geom):
                new = gpd.GeoSeries([line], index=[new_col])
                new_data.append(pd.concat([row, new]))

        new_data = gpd.GeoDataFrame(new_data, columns=col_list, geometry=col_name)

    new_data = new_data.set_geometry(new_col)
    new_data = new_data.set_crs(input_geodataframe.crs, allow_override=True)

    return new_data


def to_polygon(input_geodataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Converts a GeoDataframe with any geometry object into a GeoDataframe of Polygon geometry
       It keeps the original geometry column and adds a new one with Polygon that is set as active_geometry_name

    Args:
        input_geodataframe: GeoDataframe to be converted

    Returns:
        A GeoDataframe onlye with Polygon geometry
    """
    new_data = []
    col_name = input_geodataframe.active_geometry_name
    new_col = col_name + "2polygon"

    col_list = list(input_geodataframe.columns) + [new_col]
    first_geometry = input_geodataframe.iloc[0][col_name]

    # A naive way to identify if the dataset already contains polygons
    # TODO: some datasets have a heterogeneous geometry with Points, Lines, etc. Find a way to better test it.
    if isinstance(first_geometry, Polygon):
        return input_geodataframe

    # Handle point/line input by grouping
    if isinstance(first_geometry, (Point, LineString, MultiLineString, MultiPoint)):
        non_geom_cols = [
            col
            for col in input_geodataframe.columns
            if not isinstance(input_geodataframe[col], gpd.GeoSeries)
        ]
        grouped = input_geodataframe.groupby(non_geom_cols)[col_name]

        if isinstance(first_geometry, Point):
            polygons = grouped.apply(lambda x: Polygon(x.tolist()))
        elif isinstance(first_geometry, MultiPoint):
            polygons = grouped.apply(
                lambda x: Polygon([pt for geom in x for pt in geom.geoms])
            )
        else:  # LineString or MultiLineString
            polygons = grouped.apply(lambda x: MultiPolygon(polygonize(x.geometry)))

        new_data = gpd.GeoDataFrame(polygons.reset_index())
        new_data.columns = non_geom_cols + [new_col]
    else:
        for _, row in input_geodataframe.iterrows():
            geom = row[col_name]

            if isinstance(geom, MultiPolygon):
                for polygon in geom.geoms:
                    new = gpd.GeoSeries([polygon], index=[new_col])
                    new_data.append(pd.concat([row, new]))
        # #    elif isinstance(row[col_name], Polygon):

        new_data = gpd.GeoDataFrame(new_data, columns=col_list, geometry=col_name)

    new_data = new_data.set_geometry(new_col)
    new_data = new_data.set_crs(input_geodataframe.crs)

    return new_data


## https://gis.stackexchange.com/questions/379412/creating-geopandas-geodataframe-from-rasterio-features
def raster_to_polygon(
    raster_reader: DatasetReader,
    reduce_with: Optional[str] = None,
    band: Optional[int] = None,
    clusters: Optional[int] = None,
    aggregate_func: Optional[str] = None,
    random_state: Optional[int] = 42,
) -> gpd.GeoDataFrame:
    """Vectorize a raster data into a Polygon GeoDataFrame.
    To reduce the number of polygons, it can apply a reduce_with `quantize` or a `cluster` process controlled by band value.

     Args:
         raster_reader: a rasterio.DatasetReader with the data to be converted
         band: one of the raster_reader bands. If None, always uses band=1 when necessary.
         reduce_with: function name ('quantize' or 'cluster') to reduce the number of output polygons. 'cluster' is always KMeans
         clusters: number of bins/clusters generated by the 'reduce_with' function. Smaller values create fewer polygons. The user can try 3 or 6.
         aggregate_func: function name to aggregate values of a polygon: 'mean', 'median', 'mode', 'max', or 'min'
         random_state: Determines random number generation for K-Means centroid initialization
     Returns:
         GeoDataFrame: List of Polygon geometries associated with an (aggregated_)value

    """
    if reduce_with not in [None, "quantize", "cluster"]:
        raise TypeError(
            "reduce_with should be None or one of the follow options ['quantize', 'cluster'] "
        )
    if aggregate_func not in [None, "mean", "meadian", "mode", "max", "min"]:
        raise TypeError(
            "aggregate_func should be None or one of the follow options ['mean', 'meadian', 'mode', 'max', 'min'] "
        )
    if reduce_with == "quantize":
        band = 1 if band is None else band
    elif reduce_with == "cluster":
        band = None
    if reduce_with is not None:
        clusters = 3 if clusters is None else clusters
        aggregate_func = "mean" if aggregate_func is None else aggregate_func
        random_state = 42 if random_state is None else random_state

    data = raster_reader.read(band)
    data_mask = data != raster_reader.nodata

    if reduce_with == "quantize":
        data = np.digitize(
            data, bins=np.linspace(np.nanmin(data), np.nanmax(data), clusters)
        ).astype(data.dtype)
        data_mask = ~np.isnan(data)
    elif reduce_with == "cluster":
        pixels = data
        data_shape = pixels.shape[1:]
        pixels = pixels.reshape((pixels.shape[0], -1))
        pixels = np.transpose(pixels, axes=[1, 0])

        model = KMeans(n_clusters=clusters, random_state=random_state)
        model.fit(pixels)

        data = model.labels_.reshape(data_shape)
        data_mask = None

    extracted_shapes = features.shapes(
        data, mask=data_mask, transform=raster_reader.transform
    )

    geometry = []
    cluster = []
    aggregated_value = []

    for geom, val in extracted_shapes:
        geometry.append(shape(geom))

        if reduce_with is None:
            aggregated_value.append(val)
        else:
            cluster.append(val)

            out_image, _ = mask.mask(raster_reader, [mapping(geometry[-1])], crop=True)
            values = out_image[0].flatten()
            values = values[~np.isnan(values)]

            if aggregate_func == "mean":
                aggregated_value.append(np.mean(values) if len(values) else np.nan)
            elif aggregate_func == "median":
                aggregated_value.append(np.median(values) if len(values) else np.nan)
            elif aggregate_func == "mode":
                aggregated_value.append(
                    scipy.stats.mode(values)[0] if len(values) else np.nan
                )
            elif aggregate_func == "max":
                aggregated_value.append(np.max(values) if len(values) else np.nan)
            elif aggregate_func == "min":
                aggregated_value.append(np.min(values) if len(values) else np.nan)

    if len(cluster) > 0:
        gdf_raster = gpd.GeoDataFrame(
            {"cluster": cluster, "aggregated_value": aggregated_value},
            geometry=geometry,
            crs=raster_reader.crs,
        )
    else:
        gdf_raster = gpd.GeoDataFrame(
            {"value": aggregated_value}, geometry=geometry, crs=raster_reader.crs
        )

    return gdf_raster


def vector_to_raster(
    input_geodataframe: gpd.GeoDataFrame,
    feature_column: str,
    resolution: Optional[Union[float, Tuple[float]]] = None,
    size: Optional[Union[int, Tuple[int]]] = None,
    epsilon: Optional[float] = 1e-9,
) -> Tuple[np.ndarray, Affine, Tuple]:
    """Rasterize a vector data

    Args:
        input_geodataframe: a GeoDataFrame with the data to be converted
        feature_column: data column used to populate the raster values
        resolution: a factor that divides data dimensions, raster cell size. It is dependent on the input_geodataframe coordinate system
        size: a tuple with (width, height) of the output raster. It is easier to use because it does not depend on the coordinate system
        epsilon: used to adjust raster boundaries so as not to lose data information
    Returns:
        np.array: generated raster matrix
        affine.Affine: transformation associated with the data
        tuple: positions (left, right, bottom, top) used to generate the raster

    """
    left, bottom, right, top = input_geodataframe.total_bounds

    left -= epsilon
    bottom -= epsilon
    right += epsilon
    top += epsilon

    if (resolution is None and size is None) or (
        resolution is not None and size is not None
    ):
        raise TypeError("Define resolution OR size")
    if size is not None and (not isinstance(size, tuple) or len(size) != 2):
        raise TypeError("size should be a tuple with only two positions")

    if resolution:
        width = math.ceil((right - left) / resolution)
        height = math.ceil((top - bottom) / resolution)
    else:
        width, height = size

    transform = from_bounds(left, bottom, right, top, width, height)

    shapes = (
        (geom, value)
        for geom, value in zip(
            input_geodataframe.geometry, input_geodataframe[feature_column]
        )
    )

    output_raster = features.rasterize(
        shapes=shapes,
        out_shape=(height, width),
        transform=transform,
        all_touched=True,
        merge_alg=MergeAlg.add,
        fill=0,
        dtype=input_geodataframe[feature_column].dtype,
        # fill=np.nan,
        # dtype=rasterio.float32,
    )

    return output_raster, transform, (left, right, bottom, top)


def create_grid(
    bounds: List[float],
    crs: Optional[str] = DEFAULT_CRS,
    resolution: Optional[Union[float, Tuple[float]]] = None,
    size: Optional[Union[int, Tuple[int]]] = None,
    epsilon: Optional[float] = 1e-9,
) -> gpd.GeoDataFrame:
    """Creates a grid of polygons with a specific bound and CRS

    Args:
        bounds: the grid boundaries
        crs: a specific coordinate reference
        resolution: a factor that divides data dimensions, raster cell size. It is dependent on the input_geodataframe coordinate system
        size: a tuple with (width, height) of the output raster. It is easier to use because it does not depend on the coordinate system
        epsilon: used to adjust raster boundaries so as not to lose data information
    Returns:
        GeoDataframe: a new GeoDataframe with polygons covering the whole original BOUNDS
    """
    left, bottom, right, top = bounds

    left -= epsilon
    bottom -= epsilon
    right += epsilon
    top += epsilon

    if (resolution is None and size is None) or (
        resolution is not None and size is not None
    ):
        raise TypeError("Define resolutions OR size")
    if size is not None and (isinstance(size, tuple) and len(size) != 2):
        raise TypeError("size should be a tuple with only two positions")
    if resolution is not None and (
        isinstance(resolution, tuple) and len(resolution) != 2
    ):
        raise TypeError(
            "resolution should be a NUMBER or a TUPLE with only two positions"
        )

    if resolution is not None:
        if isinstance(resolution, tuple):
            x_resolution, y_resolution = resolution
        else:
            x_resolution = y_resolution = resolution
    if size is not None:
        if isinstance(size, tuple):
            width, height = size
        else:
            width = height = size

        x_resolution = (right - left) / width
        y_resolution = (top - bottom) / height

    grid_cells = []

    indices = {"i": [], "j": []}

    for i, x in enumerate(np.arange(left, right, x_resolution)):
        for j, y in enumerate(np.arange(bottom, top, y_resolution)):
            indices["i"].append(i)
            indices["j"].append(j)
            grid_cells.append(box(x, y, x + x_resolution, y + y_resolution))

    return gpd.GeoDataFrame(pd.DataFrame(indices), geometry=grid_cells, crs=crs)


def grid_from_data(
    input_geodataframe: gpd.GeoDataFrame,
    resolution: Optional[Union[float, Tuple[float]]] = None,
    size: Optional[Union[int, Tuple[int]]] = None,
    bounds: Optional[List[float]] = None,
    epsilon: Optional[float] = 1e-9,
    column_map: Optional[str] = None,
) -> gpd.GeoDataFrame:
    """Creates a grid of polygons around a GeoDataframe and maps the dataframe data into the polygons

    Args:
        input_geodataframe: a GeoDataFrame with the data to be converted
        feature_column: data column used to populate the raster values
        resolution: a factor that divides data dimensions, raster cell size. It is dependent on the input_geodataframe coordinate system
        size: a tuple with (width, height) of the output raster. It is easier to use because it does not depend on the coordinate system
        bounds: the grid boundaries
        epsilon: used to adjust raster boundaries so as not to lose data information
        column_map: an  input_geodataframe to be mapped as the output value. If None, the output dataframe returns only a count of items.
    Returns:
        GeoDataframe: a new GeoDataframe with polygons covering the whole original area

    """
    bounds = input_geodataframe.total_bounds if bounds is None else bounds
    grid_gdf = create_grid(
        bounds=bounds,
        crs=input_geodataframe.crs,
        resolution=resolution,
        size=size,
        epsilon=epsilon,
    )
    joined = gpd.sjoin(input_geodataframe, grid_gdf, how="left", predicate="intersects")

    if column_map is None:
        grouped = joined.groupby("index_right")
        values = grouped.apply(len, include_groups=False).astype(float)
        grid_gdf["value"] = values
    else:
        joined = joined.drop_duplicates(subset=["index_right"])
        joined = joined[["index_right"] + [column_map]].set_index("index_right")
        joined = joined.reindex(grid_gdf.index, fill_value=np.nan)
        grid_gdf["value"] = joined

    return grid_gdf
