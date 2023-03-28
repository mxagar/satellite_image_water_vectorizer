"""This module contains several functions to
process geospatial rasters. Specifically,
these functions are implemented and documented:

    resample_persist_band()
    resample_bands()
    crop_persist_band()
    crop_bands()
    load_band_image()
    load_bands()
    compute_ndvi()
    compute_ndwi()
    generate_persist_ndmap()

Pylint: 9.29/10.

Author: Mikel Sagardia
Date: 2023-03-27
"""

#import sys
import os
import logging
from glob import glob

import numpy as np
#import pandas as pd
#import geopandas as gpd
#import matplotlib.pyplot as plt

import rasterio as rio
from rasterio.mask import mask
from rasterio.transform import Affine

from .resample_raster import resample_res

# Logging configuration
logging.basicConfig(
    filename='./geo_processing.log', # filename, where it's dumped
    level=logging.INFO, # minimum level I log
    filemode='a', # append
    format='%(name)s - %(asctime)s - %(levelname)s - %(message)s')
    # add function/module name for tracing
# Thi will be imported in the rest of the modules
logger = logging.getLogger()


# FIXME: refactor to two functions: resample & persist and use persistence manager
def resample_persist_band(input_path,
                          output_path,
                          resolution=(60,60)):
    """Resample band pixelmap to specified resolution
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


def resample_bands(band_paths,
                   resolution=(60,60),
                   output_folder="processed"):
    """Resample band pixelmaps to specified resolution
    and persist them all. This function uses resample_persist_band().

    Args:
        band_paths (list[str]): list of all band paths.
        resolution (tuple[number], optional): x and y resolution to resample.
            Defaults to (60,60).
        output_folder (str): local folder into which resampled bands are saved.
            Defaults to "processed".

    Returns: None.
    """
    # Extract scene path
    scene_path = os.path.join(*band_paths[0].split(os.sep)[:-1])

    # FIXME: refactor to function?
    # Create a folder to store all processed images images
    try:
        output_path = os.path.join(scene_path, output_folder)
        os.mkdir(output_path)
    except FileExistsError as err:
        logger.info("resample_bands: processing output folder already exists: %s",
                    output_folder)

    # Resample and save all files
    for band in band_paths:
        input_file = band
        filename = input_file.split(os.sep)[-1]
        output_file = os.path.join(scene_path, output_folder, filename)
        try:
            assert os.path.isfile(input_file)
            resample_persist_band(input_path=input_file,
                                  output_path=output_file,
                                  resolution=resolution)
        except AssertionError as err:
            logger.error("resample_bands: input_file does not exist: %s",
                         input_file)
            raise err

    logger.info("resample_bands: bands correctly resampled and persisted!")


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
    with rio.open(input_path, "r") as src:
        out_image, out_transform = mask(src,
                                        shapes,
                                        crop=True)
        out_meta = src.meta
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        with rio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)

    return out_image, out_meta


def crop_bands(band_paths,
               gdf_bbox,
               output_folder="processed"):
    """Load bands from provided paths,
    crop them according to the geometries in gdf_bbox
    and persist them to the output_folder.
    This function uses crop_persist_band().

    Args:
        band_paths (_type_): paths of the band files
        gdf_bbox (gepandas.GeoSeries): iterable with geometries to crop.
        output_folder (str): local folder into which resampled bands are saved.
            Defaults to "processed".

    Returns: None.
    """
    # Extract scene path
    scene_path = os.path.join(*band_paths[0].split(os.sep)[:-1])

    # FIXME: refactor to function?
    # Create a folder to store all processed images images
    try:
        output_path = os.path.join(scene_path, output_folder)
        os.mkdir(output_path)
    except FileExistsError as err:
        logger.info("crop_bands: processing output folder already exists: %s",
                    output_folder)

    # Crop all bands
    for band in band_paths:
        input_file = band
        filename = input_file.split(os.sep)[-1]
        output_file = os.path.join(scene_path, output_folder, filename)
        try:
            assert os.path.isfile(input_file)
            _, _ = crop_persist_band(input_path=input_file,
                                     output_path=output_file,
                                     shapes=gdf_bbox)
        except AssertionError as err:
            logger.error("resample_bands: input_file does not exist: %s",
                         input_file)
            raise err

    logger.info("crop_bands: bands correctly cropped and persisted!")


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


def load_bands(scene_path):
    """Load band files as numpy arrays from a given
    scene path which contains the files. Band files must have
    the filename `*B?*.tiff`, being `?` the correct band number.
    This function uses load_band_image().

    Args:
        scene_path (str): path which contains the band files to be loaded.

    Returns:
        band_arrays (numpy.ndarray): numpy array with band pixelmaps
            with the shape (num_bands, width, height).
        band_names (list[str]): band types/names: 1, 2, 3, ..., 12, 8A.
        profile (dict): profile of the band files.
    """
    # Extract band paths
    band_paths = glob(os.path.join(scene_path, "*B?*.tiff"))
    band_paths.sort()

    # Check we have files
    try:
        assert len(band_paths) > 0
    except AssertionError as err:
        logger.error("load_bands: no (valid) band data in provided path: %s",
                     scene_path)
        raise err

    # Iterate through all files and load them
    images = []
    profiles = []
    band_names = []
    for band_filename in band_paths:
        try:
            assert os.path.isfile(band_filename)
            img, profile, band_name = load_band_image(filename=band_filename,
                                                      resample=False)
            images.append(img)
            profiles.append(profile)
            band_names.append(band_name)        
        except AssertionError as err:
            logger.error("load_bands: no (valid) band data in provided path: %s",
                        scene_path)
            raise err

    # Check: are they all resampled to the same size?
    _, w, h = images[0].shape
    try:
        for i in images:
            assert i.shape[1] == w
            assert i.shape[2] == h
    except AssertionError as err:
        logger.error("load_bands: band pixelmaps have different sizes.")
        raise err

    # Stack all image channels/bands: (band, width, height)
    band_arrays = np.stack(images).squeeze()

    # Pick one profile
    profile = profiles[0]

    logger.info("load_bands: bands + meta-data correctly loaded!")

    return band_arrays, band_names, profile


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

    # FIXME: use exception handling, as before
    # Store if we obtained something from compute_ndvi
    if ndmap.any() or ndmap_profile:    
        # Create new profile for NDVI image
        ndmap_profile = profile.copy()
        ndmap_profile['count'] = 1
        ndmap_profile['dtype'] = 'float32'
        ndmap_profile['nodata'] = -9999

        # Create a transform for the NDVI image
        transform = profile['transform']
        ndmap_transform = Affine(transform.a,
                                 transform.b,
                                 transform.c,
                                 transform.d,
                                 transform.e,
                                 transform.f)

        # Write the NDVI image to disk
        with rio.open(output_path, 'w', **ndmap_profile) as ndmap_ds:
            ndmap_ds.write(ndmap, 1)
            ndmap_ds.transform = ndmap_transform

        logger.info("generate_persist_ndvi: %s correctly generated and saved.", map_type)

    else:
        logger.warning("generate_persist_ndvi: bands are missing to compute NDVI/NDWI.")

    return ndmap, ndmap_profile
