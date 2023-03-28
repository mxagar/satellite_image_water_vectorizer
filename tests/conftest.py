'''Testing configuration module for Pytest.
This file is read by pytest and the fixtures
defined in it are used in all the tested files.

Note that this module defines where
the testing rasters are; if the rasters are elsewhere,
simply modify the paths. In a regular situation
we could improve that defining and using
a config_test.yaml file

Author: Mikel Sagardia
Date: 2023-03-27
'''
import pytest

import geo_toolkit as gt
from geo_toolkit import __version__ as geo_lib_version

# Fixtures of the geo_toolkit package functions.
# Fixtures are predefined variables passed to test functions;
# in this case, most variables are functions/classes to be tested.

## -- Library Parameters

@pytest.fixture
def config_filename():
    '''Configuration filename.'''
    return "config_test.yaml"

@pytest.fixture
def data_path():
    '''Data path with rasters.'''
    return pytest.config_dict["data_path"]

@pytest.fixture
def resolution():
    '''Resampling resolution.'''
    return tuple(pytest.config_dict["resolution"])

@pytest.fixture
def output_folder():
    '''Output folder within data_path.'''
    return pytest.config_dict["output_folder"]

@pytest.fixture
def logger():
    '''Logger.'''
    return gt.logger

@pytest.fixture
def lib_version():
    '''geo_toolkit version.'''
    return geo_lib_version

## -- Library Functions

@pytest.fixture
def resample_persist_band():
    '''resample_persist_band() function from geo_toolkit.'''
    return gt.resample_persist_band

@pytest.fixture
def resample_bands():
    '''resample_bands() function from geo_toolkit.'''
    return gt.resample_bands

## -- Variable plug-ins

def config_dict_plugin():
    '''Initialize pytest project config container as None:
    pytest.config_dict: dict'''
    return None

def pytest_configure():
    '''Create objects in namespace:
    - `pytest.config_dict`
    '''
    pytest.config_dict = config_dict_plugin()
