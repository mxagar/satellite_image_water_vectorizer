"""

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


if __name__ == '__main__':
    pass