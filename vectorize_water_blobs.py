"""This module uses the geo_toolkit library/package
to implement an application in which water blobs
in a Sentinel 2 band set are vectorized.

Pylint: 8.99/10.

Author: Mikel Sagardia
Date: 2023-03-27
"""
import os
from glob import glob

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

import rasterio
import rasterio.plot
from rasterio.features import shapes

from shapely.geometry import box
from shapely.geometry import shape

from geo_toolkit import (
    logger,
    resample_bands,
    crop_bands,
    load_bands,
    generate_persist_ndmap
)

if __name__ == '__main__':

    ## -- Initialization: Constants, Variables, CRS, etc.

    # Choose the scene number
    SCENE = 1
    #SCENE = 2

    # These paths should contain the contents of the original challenge
    DATA_PATH = "./data/"
    SCENE_1_PATH = DATA_PATH + "Scene 1 - S2A_MSIL1C_20230223T112111_N0509_R037_T30UVF_20230223T145910"
    SCENE_2_PATH = DATA_PATH + "Scene 2 - S2B_MSIL1C_20230102T113359_N0509_R080_T30UWG_20230102T121121"
    OUTPUT_FOLDER = "processed"

    # Lng/Lat format in EPSG:4326 - WGS84, located in the UK
    SCENE_1_BBOX = [-3.480290297664652, 54.26510479276385, -2.9010711619639267, 54.61995328561707]
    SCENE_2_BBOX = [-2.815247, 55.102730, -1.450195, 55.553495]

    SCENE_PATH = SCENE_1_PATH
    SCENE_BBOX = SCENE_1_BBOX
    if SCENE == 2:
        SCENE_PATH = SCENE_2_PATH
        SCENE_BBOX = SCENE_2_BBOX

    # Create a GeoSeries with the ROI
    bbox = box(minx=SCENE_BBOX[0],
               miny=SCENE_BBOX[1],
               maxx=SCENE_BBOX[2],
               maxy=SCENE_BBOX[3],
               ccw=True)
    gdf_bbox = gpd.GeoSeries([bbox], crs = 'epsg:4326')

    # Load points of interest, target (GeoJSON)
    gdf_points = gpd.read_file(os.path.join(SCENE_PATH, 'lakes.geojson'))

    # Load band filenames
    band_paths = glob(os.path.join(SCENE_PATH, "*B?*.tiff"))
    band_paths.sort()

    # Load raster src to get CRS
    with rasterio.open(band_paths[0]) as src:
        band_crs = src.crs

    # Transform all data to the same CRS
    gdf_points = gdf_points.to_crs(src.crs)
    gdf_bbox = gdf_bbox.to_crs(src.crs)

    ## -- Objective 1: Resample, Crop and Persist Rasters

    resample_bands(band_paths,
                   resolution=(60,60),
                   output_folder=OUTPUT_FOLDER)

    # Modified scene path, after resampling
    #scene_path_ = SCENE_PATH # Use un-resampled files
    scene_path_ = os.path.join(SCENE_PATH, OUTPUT_FOLDER)

    # Re-load band filenames, after resampling
    band_paths = glob(os.path.join(scene_path_, "*B?*.tiff"))
    band_paths.sort()

    crop_bands(band_paths,
               gdf_bbox,
               output_folder=".") # Re-write the resampled files
               #output_folder=OUTPUT_FOLDER) # Using un-resampled files

    band_arrays, band_names, profile = load_bands(scene_path_)

    ## -- Objective 2: Compute the NDVI and the NDWI Maps

    maps = ["ndvi", "ndwi"]
    for ndi in maps:
        output_path = os.path.join(SCENE_PATH, OUTPUT_FOLDER, ndi+".tiff")
        ndmap, ndmap_profile = generate_persist_ndmap(band_arrays,
                                                    band_names,
                                                    profile,
                                                    output_path,
                                                    map_type=ndi)

    ## -- Objective 3: Extract Water Shapes

    # Load ND-map raster file
    filename = "ndwi.tiff"
    if SCENE == 2:
        filename = "ndvi.tiff"
    ndmap_filepath = os.path.join(SCENE_PATH, OUTPUT_FOLDER, filename)

    try:
        with rasterio.open(ndmap_filepath) as ndmap_src:
            ndmap = ndmap_src.read(1)
            ndmap_transform = ndmap_src.transform
            ndmap_crs = ndmap_src.crs
    except FileNotFoundError as err:
        logger.error("main: ndmap_filepath does not exist: %s",
                     ndmap_filepath)
        raise err

    # Compute mask (thresholding)
    ndmap_threshold = 0.3
    value_mask = 1
    water_mask = None
    if SCENE == 1: # NDWI
        water_mask = np.where(ndmap > ndmap_threshold,
                              abs(value_mask-1),
                              value_mask)
    elif SCENE == 2: # NDVI
        ndmap_threshold = 0.02
        value_mask = 1
        water_mask = np.where(ndmap < ndmap_threshold,
                              value_mask,
                              abs(value_mask-1))
    logger.info("main: index map correctly masked.")

    # Generate polygons from water bodies
    water_polygons = []
    for single_water_mask, value in shapes(water_mask.astype(dtype='int16'),
                                           transform=ndmap_transform):
        if value == value_mask:
            water_polygons.append(shape(single_water_mask))
    logger.info("main: %s water polygons extracted.", str(len(water_polygons)))

    try:
        assert len(water_polygons) > 0
    except AssertionError as err:
        logger.warning("main: water_polygons is empty!")
        #raise err

    # Convert water polygons to geoseries
    water_geoseries = gpd.GeoSeries(water_polygons, crs=ndmap_crs)

    ## -- Objective 4: Identify Lake Polygons

    # Filter water body polygons:
    # take the ones which contain or are closest to the target points.
    ids = []
    polygons = []
    for i, point in gdf_points.iterrows():
        ids.append(point.id)
        if SCENE == 1:
            mask = water_geoseries.contains(point.geometry)
            polygons.append(water_geoseries[mask].values[0])
        elif SCENE == 2:
            dist = water_geoseries.distance(point.geometry)
            closest = dist.argmin()
            polygons.append(water_geoseries.loc[closest])

    # Assemble GeoDataFrame and save it
    gdf_lakes = gpd.GeoDataFrame({'id': ids, 'geometry': polygons}, crs = ndmap_crs)
    gdf_filename = os.path.join(SCENE_PATH,
                                OUTPUT_FOLDER,
                                f"scene_{SCENE}_lake_polygons.geojson")
    gdf_lakes.to_file(gdf_filename, driver='GeoJSON')
    logger.info("main: lake polygons identified and saved: %s.", gdf_filename)

    # Plot the final result:
    # masked raster + select water polygons + original target points
    fig, ax = plt.subplots(figsize=(7, 7))
    rasterio.plot.show(water_mask,
                       transform=ndmap_transform,
                       ax=ax,
                       cmap='gray')
    gdf_lakes.plot(ax=ax,
                   alpha=0.75,
                   facecolor='none',
                   edgecolor='red',
                   linewidth=2) # 10
    gdf_points.plot(ax=ax, markersize=30, color='blue')
    plt.title(f"Scene {SCENE}: Identified lake polygons + points")

    plot_filename = os.path.join(SCENE_PATH, OUTPUT_FOLDER, f"scene_{SCENE}_lake_polygons.png")
    plt.savefig(plot_filename,dpi=200,transparent=False,bbox_inches='tight')
    plt.show()
