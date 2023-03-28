'''This module tests the functions in the package
geo_toolkit using Pytest. The geo_toolkit library
contains several functions to process geospatial rasters.
The present testing module uses the fixtures defined in
conftest.py.

To install pytest:

>> python -m pip install -U pytest

The script expects the data to be located in the paths
specified in conftest.py; if they are elsewhere,
simply modify the path sin conftest.py
In a regular situation we could improve that
defining and using a config_test.yaml file loaded
in conftest.py.

NOTE: This module currently tests only one function,
resample_bands(); in the future all functions and
structures from geo_toolkit should be tested.

Pylint: 9.50/10.

Author: Mikel Sagardia
Date: 2023-03-27
'''
import os
#from os import listdir
from glob import glob
import yaml
import pytest
import rasterio

def test_resample_bands(config_filename,
                        resample_bands,
                        logger):
    """Test resample_bands() function.
    
    Args:
        config_filename (str): fixture with configuration filename.
        resample_bands (function object): resample_bands() function fixture.
        logger (object): logger fixture.

    Returns: None.
    """
    # Open testing config file/dict
    config = {}
    try:
        with open(config_filename) as f: # 'config_test.yaml'
            config = yaml.safe_load(f)
    except FileNotFoundError as err:
        logger.error("test_resample_bands: configuration YAML not found: %s.",
                     config_filename)
        raise err
    # Save config dict to pytest context/session so other functions can use it
    pytest.config_dict = config

    # Load band filenames
    band_paths = glob(os.path.join(config["data_path"], "*B?*.tiff"))
    band_paths.sort()
    try:
        assert len(band_paths) > 0
    except AssertionError as err:
        logger.error("test_resample_bands: no band rasters found in data_path: %s.",
                     config["data_path"])
        raise err

    # Run function to be tested
    resample_bands(band_paths,
                   resolution=tuple(config["resolution"]),
                   output_folder=config["output_folder"])

    # Check output from resample_bands
    # 1) Files there?
    data_path_ = os.path.join(config["data_path"], config["output_folder"])
    band_paths_ = glob(os.path.join(data_path_, "*B?*.tiff"))
    band_paths_.sort()
    try:
        assert len(band_paths_) > 0
    except AssertionError as err:
        logger.error("test_resample_bands: missing resampled band rasters!")
        raise err
    # 2) Resolution correct?
    resolution = tuple(config["resolution"])
    try:
        for raster in band_paths_:
            with rasterio.open(raster, 'r') as src:
                assert src.res[0] == resolution[0]
                assert src.res[1] == resolution[1]
    except AssertionError as err:
        logger.error("test_resample_bands: unexpected resolution!")
        raise err

    logger.info("test_resample_bands: resample_bands() successfully tested.")
