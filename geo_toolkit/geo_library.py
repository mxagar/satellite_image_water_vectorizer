"""This module contains several functions to
process geospatial rasters.

Author: Mikel Sagardia
Date: 2023-03-27
"""

import sys
import os
import logging
from glob import glob

import numpy as np
import pandas as pd
import geopandas as gpd
import contextily
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
from earthpy.spatial import bytescale

import rasterio as rio
from rasterio.windows import Window
from rasterio.transform import Affine
from rasterio.features import shapes
from rasterio.plot import plotting_extent
from rasterio.plot import show
from rasterio.plot import reshape_as_raster, reshape_as_image

from shapely.geometry import box
from shapely.geometry import shape

from .resample_raster import resample_res, resample_scale

# Logging configuration
logging.basicConfig(
    filename='./geo_processing.log', # filename, where it's dumped
    level=logging.INFO, # minimum level I log
    filemode='w', # append
    format='%(name)s - %(asctime)s - %(levelname)s - %(message)s')
    # add function/module name for tracing
# Thi will be imported in the rest of the modules
logger = logging.getLogger()


# FIXME: refactor to two functions: resample & persist and use persistence manager
def resample_persist_band(input_path,
                          output_path,
                          resolution=(60,60)):
    """Resample band pixelmap to spcified resolution
    and persist.
    
    Args:
        input_path (str): input filename of the band/channel image pixelmap
        output_path (str): output filename of the band/channel image pixelmap
        resolution (tuple[float]): x and y resolution to resample

    Returns: None
    """
    xres = resolution[0]
    yres = resolution[1]
    with rio.open(input_path, 'r') as src:
        img, profile = resample_res(src, xres, yres)
    
    with rio.open(output_path, "w", **profile) as dataset:
        dataset.write(img)


# FIXME: refactor to two functions: crop & persist and use persistence manager
def crop_persist_band(input_path, output_path, shapes):
    """Load band from input path,
    crop it according to the geometries in shapes
    and persist to filepath in output_path.
    
    Args:
        input_path (str): path of the band file
        output_path (str): path to persist cropped band
        shapes (gepandas.GeoSeries): iterable with geometries to crop
    
    Returns:
        out_image (numpy.ndarray): copped image/band array
        out_meta (dict): dictionary with band information
            (i.e., CRS, affine transformation matrix, etc.)
    """
    with rio.open(input_file, "r") as src:
        out_image, out_transform = rio.mask.mask(src,
                                                 shapes,
                                                 crop=True)
        out_meta = src.meta
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        with rio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image)
        
    return out_image, out_meta


def load_band_image(filename, resample=False, resolution=(60,60)):
    """Load a band file and resample (resize) it
    if required.
    
    Args:
        filename (str): filename of the band/channel image pixelmap
        resample (bool): resample/resize or not (default: False)
        resolution (tuple[float]): x and y resolution to resample
            (default: (60,60))

    Returns:
        img (numpy.ndarray): band array, image
        profile (dict): dictionary with band profile meta-info
        band_name (str): band name (1, 2, ...)
    """
    xres = resolution[0]
    yres = resolution[1]
    resample = True
    # FIXME: use regex in future, or a more generic way...
    band_name = filename.split(os.sep)[-1][1:3]
    with rio.open(filename, 'r') as src:
        img = None
        profile = None
        if resample:
            img, profile = resample_res(src, xres, yres)
        else:
            img, profile = src.read(1), src.profile

    return img, profile, band_name


def compute_ndvi(images, band_names):
    """Compute the Normalized Difference
    Vegetation Index (NDVI) pixelmap.

    NDVI = (NIR - Red) / (NIR + Red)
         = (B8 - B4) / (B8 + B4)

    Args:
        images (numpy.ndarray): array with images
            in a 3D shape: band, width, height
        band_names (list[str]): band names associated
            to the images, e.g.: ['01', '02', ..., '08A']

    Returns:
        ndvi (numpy.ndarray): NDVI pixelmap
    """
    # Initialize
    red_idx = None
    nir_idx = None
    ndvi = None

    # Get the indices of the Red and NIR bands
    red_idx = band_names.index('04') if '04' in band_names else None
    nir_idx = band_names.index('08') if '08' in band_names else None

    # Get the corresponding bands
    if red_idx and nir_idx:
        red_band = images[red_idx].squeeze()
        nir_band = images[nir_idx].squeeze()

        # Compute NDVI; default fivision by 0 to 0
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = np.nan_to_num((nir_band - red_band) / (nir_band + red_band))

    return ndvi


def compute_ndwi(images, band_names):
    """Compute the Normalized Difference Water
    Index (NDWI) pixelmap.

    NDWI = (Green - NIR) / (Green + NIR)
         = (B3 - B8) / (B3 + B8)

    or, in the absence of Green (B3)
        
    NDWI = (NIR - SWIR) / (NIR + SWIR) (approx.)
         = (B8A - B12) / (B8A + B12) (approx.)
         = (B8A - B11) / (B8A + B11) (approx.

    Args:
        images (numpy.ndarray): array with images
            in a 3D shape: band, width, height
        band_names (list[str]): band names associated
            to the images, e.g.: ['01', '02', ..., '08A']

    Returns:
        ndwi (numpy.ndarray): NDWI pixelmap
    """
    # Initialize
    green_idx = None
    nir_idx = None
    swir_idx = None
    swir_12_idx = None
    swir_11_idx = None
    ndwi = None
    standard = False
    
    # Get the indices of the Red and NIR bands
    green_idx = band_names.index('03') if '03' in band_names else None
    nir_idx = band_names.index('8A') if '8A' in band_names else None
    swir_idx = band_names.index('12') if '12' in band_names else None
    swir_11_idx = band_names.index('11') if '11' in band_names else None

    # Select formula with available
    if green_idx and nir_idx:
        standard = True
    else:
        if swir_12_idx:
            swir_idx = swir_12_idx
        elif swir_11_idx:
            swir_idx = swir_11_idx
    
    if standard:
        # NDWI = (Green - NIR) / (Green + NIR)
        green_band = images[green_idx].squeeze()
        nir_band = images[nir_idx].squeeze()

        # Compute NDWI; default fivision by 0 to 0
        with np.errstate(divide='ignore', invalid='ignore'):
            ndwi = np.nan_to_num((green_band - nir_band) / (green_band + nir_band))
            
    elif swir_idx:
        # NDWI = (NIR - SWIR) / (NIR + SWIR) (approx.)
        swir_band = images[swir_idx].squeeze()
        nir_band = images[nir_idx].squeeze()

        # Compute NDWI; default fivision by 0 to 0
        with np.errstate(divide='ignore', invalid='ignore'):
            ndwi = np.nan_to_num((nir_band - swir_band) / (nir_band - swir_band))

    return ndwi


def generate_persist_ndmap(images,
                           band_names,
                           profile,
                           output_path,
                           map_type="ndvi"):
    """Compute and store a normalized difference map,
    either:
    
    - Normalized Difference Vegetation Index (NDVI), or
    - Normalized Difference Water Index (NDWI)
    
    Args:
        images (numpy.ndarray): array with images
            in a 3D shape: band, width, height
        band_names (list[str]): band names associated
            to the images, e.g.: ['01', '02', ..., '08A']
        profile (dict): profile dictionary of the source bands
        output_path (str): file path to persist the NDVI pixelmap
        map_type (str): "ndvi" for NDVI, "ndwi" for NDWI

    Returns:
        ndmap (numpy.ndarray): ND pixelmap
        ndmap_profile (dict) profile dictionary of the ND pixelmap
    """
    # Initialize
    ndmap = None
    ndmap_profile = None
    
    # Compute NDVI
    if map_type == "ndvi":
        ndmap = compute_ndvi(images, band_names)
    elif map_type == "ndwi":
        ndmap = compute_ndwi(images, band_names)
    else:
        print(f"generate_persist_ndmap: not valid map_type: {map_type}")

    # Store if we obtained something from compute_ndvi
    if ndmap.any() or ndmap_profile:    
        # Create new profile for NDVI image
        ndmap_profile = profile.copy()
        ndmap_profile['count'] = 1
        ndmap_profile['dtype'] = 'float32'
        ndmap_profile['nodata'] = -9999

        # Create a transform for the NDVI image
        transform = profile['transform']
        ndmap_transform = Affine(transform.a, transform.b, transform.c, transform.d, transform.e, transform.f)

        # Write the NDVI image to disk
        with rio.open(output_path, 'w', **ndmap_profile) as ndmap_ds:
            ndmap_ds.write(ndmap, 1)
            ndmap_ds.transform = ndmap_transform
    else:
        print("generate_persist_ndvi: bands are missing to compute NDVI.")
    
    return ndmap, ndmap_profile
