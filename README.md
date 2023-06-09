# Water Body Vectorization in Satellite Images

In this mini-project, two scenes captured by the Sentinel 2 satellite are processed to end up with vectorized water bodies contained in them (the lakes of [Chiemsee](https://en.wikipedia.org/wiki/Chiemsee), [Ammersee](https://en.wikipedia.org/wiki/Ammersee) and [Starnbergersee](https://de.wikipedia.org/wiki/Starnberger_See)). The data for each scene consists of the usual 13 raster bands as well as a Region of Interest (ROI) and a set of target points; each ROI contains the water bodies to vectorize and the points are inside in the water bodies. The vectorization is performed following these steps:

1. Crop all the bands in each scene to their associated ROI.
2. Compute the NDVI and NDWI maps of the cropped bands.
3. Extract the inland water body shapes in the cropped bands.
4. Identify the shapes of the water bodies associated with the provided sets of points and store them in a vectorized format.

This figure shows the RGB image of the scene 1 and its final result (step 4):

<p style="text-align:center">
  <img src="./assets/scene_1.jpg" alt="RGB image of scene 1." width=300px>
  <img src="./assets/scene_1_lake_polygons.png" alt="Identified water body (lake) polygons of scene 1." width=300px>
</p>

The remainder of this document explains the structure of the repository, how to use it and the reasoning behind the performed analysis to accomplish all steps.

:warning: **Important**: the preliminary result files are located in [`results`](results):

- Scene 1 works properly.
- Scene 2 need more fine tuning; also, alternative approaches could be used with it, as explained in the section [Step 3: Extract Water Shapes](#step-3-extract-water-shapes).

## Table of Contents

- [Water Body Vectorization in Satellite Images](#water-body-vectorization-in-satellite-images)
  - [Table of Contents](#table-of-contents)
  - [User Guide](#user-guide)
    - [Getting the Data](#getting-the-data)
    - [Installing Dependencies for Custom Environments](#installing-dependencies-for-custom-environments)
    - [Running the Notebook](#running-the-notebook)
    - [Run the Python Application Script](#run-the-python-application-script)
  - [Dataset and Preliminary Exploration](#dataset-and-preliminary-exploration)
    - [Scene 1](#scene-1)
    - [Scene 2](#scene-2)
  - [Notes on the Solution](#notes-on-the-solution)
    - [Step 1: Resample, Crop and Persist Rasters](#step-1-resample-crop-and-persist-rasters)
    - [Step 2: Compute the NDVI and the NDWI Maps](#step-2-compute-the-ndvi-and-the-ndwi-maps)
    - [Step 3: Extract Water Shapes](#step-3-extract-water-shapes)
    - [Step 4: Identify Lake Polygons](#step-4-identify-lake-polygons)
    - [Production Environment](#production-environment)
    - [Summary and Conclusions](#summary-and-conclusions)
  - [Limitations, Improvements](#limitations-improvements)
  - [References, Links and Assets](#references-links-and-assets)
  - [Terms of Use, Authorship and License](#terms-of-use-authorship-and-license)

## User Guide

The directory of the project consists of the following files:

```
.
├── LICENSE.md
├── README.md                                   # Documentation + report
├── assets/                                     # Images used in the report, etc.
│   └── ...
├── conda.yaml                                  # Conda environment file (better, use requirements.txt)
├── config_test.yaml
├── data                                        # Original dataset, to be downloaded
│   ├── Scene 1 ...
│       ├── T32UQU_20230207T101109_B01_20m.jp2
│       ├── ...
│       ├── T32UQU_20230207T101109_B8A_20m.jp2
│   │   ├── lakes.geojson
│   │   └── processed/                          # Outcomes from processing
│   │       └── ...
│   └── Scene 2 ...
│   │   ├── T32UPU_20230322T101649_B01_20m.jp2
│   │   ├── ...
│   │   ├── T32UPU_20230322T101649_B8A_20m.jp2
│       ├── lakes.geojson
│       └── processed/                          # Outcomes from processing
│           └── ...
├── geo_processing.log                          # Logs
├── geo_toolkit                                 # Library/package
│   ├── __init__.py
│   ├── geo_library.py
│   └── resample_raster.py
├── notebooks                                   # Research environment notebook
│   ├── Setup.ipynb
│   └── Geospatial_Image_Analysis.ipynb
├── requirements.txt                            # Environment dependencies
├── results                                     # Final results, taken from data/.../processed
│   ├── scene_1/
│   │   ├── T32UQU_20230207T101109_B01_20m.tiff
│   │   ├── ...
│   │   ├── T32UQU_20230207T101109_B8A_20m.tiff
│   │   ├── ndvi.tiff
│   │   ├── ndwi.tiff
│   │   ├── scene_1_lake_polygons.geojson
│   │   └── scene_1_lake_polygons.png
│   └── scene_2
│       ├── T32UPU_20230322T101649_B01_20m.tiff
│       ├── ...
│       ├── T32UPU_20230322T101649_B8A_20m.tiff
│       ├── ndvi.tiff
│       ├── ndwi.tiff
│       ├── scene_2_lake_polygons.geojson
│       └── scene_2_lake_polygons.png
├── setup.py                                    # Package installation file
├── tests                                       # Pytest tests for the package
│   ├── __init__.py
│   ├── conftest.py
│   └── test_geo_library.py
├── utils                                       # Resampling utility script
│   └── resample_raster.py
└── vectorize_water_blobs.py                    # Main application file to use the library
```

The final result files related to the 4 steps are located in the folder [`results`](./results/); additionally, the present `README.md` contains the documentation of the project as well as the report with the learned insights.

After setting up the correct environment, there are two ways of using/running the project:

1. Open the notebook [`Geospatial_Image_Analysis.ipynb`](notebooks/Geospatial_Image_Analysis.ipynb) and execute all cells in sequence. The variable `SCENE` needs to be set at the beginning to run the processing for each of the scenes 1 or 2. The notebook guides the user with comments and text about the followed reasoning.
2. Run the script [`vectorize_water_blobs.py`](vectorize_water_blobs.py) which uses the library [`geo_toolkit`](geo_toolkit) to perform the same processing. The outcome is the same as with the notebook, but in this case the code has been transformed to a production environment following PEP8 conventions, logging, etc. In the script, the `SCENE` needs to be selected, too.

In the following sub-sections, practical commands for setting up the environment and running the application are shown.

### Getting the Data

The dataset is not committed to the Github repository due its large size; however, you can download it from this link:

[https://drive.google.com/drive/folders/1u9zbYNrakPoNVV6bhDj9U2TDEmAAT_Bw?usp=share_link](https://drive.google.com/drive/folders/1u9zbYNrakPoNVV6bhDj9U2TDEmAAT_Bw?usp=share_link)

The folders `scene_1` and `scene_2` should be placed in the local folder `data/`.

Also, note that you can manually download your own dataset from [Copernicus](https://scihub.copernicus.eu). A detailed guide on how to do it can be obtained [here](https://gisgeography.com/how-to-download-sentinel-satellite-data/).

The notebook [`Setup.ipynb`](./notebooks/Setup.ipynb) performs a preliminary analysis of the satellite bands; additionally, the Regions of Interest (ROIs) and target lake points are defined in that notebook after a visual inspection of the scenes. 

### Installing Dependencies for Custom Environments

First, we need to install:

- A python package environment manager, such as [Anaconda/Miniconda](https://docs.conda.io/en/latest/miniconda.html). Alternatively, we can use the default [venv](https://docs.python.org/3/library/venv.html).
- [GDAL](https://gdal.org); a practical guide can be found [here](https://towardsdatascience.com/spatial-data-science-installing-gdal-on-windows-and-macos-6fb5c958dc26).

Then, we need to create a custom environment and install the required dependencies; for instance, a quick recipe which sets everything up with Anaconda is the following:

```bash
# Create an environment and install the dependencies
conda create --name cosmos pip python=3.10
conda activate cosmos
python -m pip install -r requirements.txt
# Install the geo_toolkit library
python -m pip install .
```

List of the most relevant dependencies installed with `requirements.txt` (see versions in the file):

- GDAL
- Numpy
- Pandas
- Matplotlib
- GeoPandas
- Earthpy
- Rasterio
- Shapely

All these libraries are open source and support the most common formats, as required in the challenge description.

### Running the Notebook

Assuming all the dependencies have been installed, open a terminal and execute these commands:

```bash
cd notebooks
jupyter lab .
# Open Geospatial_Image_Analysis.ipynb
```

The notebook guides us. First, we need to choose the value for `SCENE` and then we can execute the cells in sequence. The resulting files are persisted in the `processed` folder of each scene.

### Run the Python Application Script

Assuming all the dependencies have been installed, open a terminal and execute these commands:

```bash
python vectorize_water_blobs.py
# Wait for execution
# Final image appears
# geo_processing.log contains logging info
```

There is no guiding, but the code has been transformed to a production environment. Similarly, the resulting files are persisted in the `processed` folder of each scene.

NOTE: Here also, we need to choose the value for `SCENE` in the `vectorize_water_blobs.py` script.

## Dataset and Preliminary Exploration

The dataset consists of two scenes from south Germany captured by Sentinel 2; these are composed by raster bands with the typical resolutions, ranging from 10m - 60m.

In the following, a brief description of each scene is provided.

### Scene 1

Scene 1 consists of the regular 13 [bands captured by Sentinel 2](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/resolutions/spectral). Additionally, a region of interest (ROI) with the following coordinates is defined manually in [`Setup.ipynb`](./notebooks/Setup.ipynb):

```python
# lng/lat format in EPSG:4326
SCENE_1_BBOX = [12.276740855204856, 47.76998650888808, 12.830008478699462, 48.06602436853697]
```

The associated file `lakes.geojson` contains 1 point contained in that ROI and centered in the clearly visible lake of [Chiemsee](https://en.wikipedia.org/wiki/Chiemsee).

After transforming all the data into the CRS of the bands (`EPSG:32632`), a plot of the pixelmaps and their gray-value distributions (histograms) shows that we have data with enough quality to work towards the goal of finding the lake.

<p style="text-align:center">
  <img src="./assets/scene_1_bands.jpg" alt="Scene 1: Bands." width=500px>
  <img src="./assets/scene_1_histograms.jpg" alt="Scene 1: Histograms." width=500px>
</p>

### Scene 2

Scene 2 is analogous to scene 1, but it contains the lakes of [Ammersee](https://en.wikipedia.org/wiki/Ammersee) and [Starnbergersee](https://de.wikipedia.org/wiki/Starnberger_See), marked with points defined in the associated file `lakes.geojson`; the ROI is:

```python
# lng/lat format in EPSG:4326
SCENE_2_BBOX = [10.9448829067118, 47.73548843800481, 11.393297391882829, 48.143490914959585]
```

Again, we need to transform all the data into the CRS of the bands (`EPSG:32632`). Next figures show a plot of the pixelmaps and their gray-value distributions (histograms).

<p style="text-align:center">
  <img src="./assets/scene_2_bands.jpg" alt="Scene 2: Bands." width=500px>
  <img src="./assets/scene_2_histograms.jpg" alt="Scene 2: Histograms." width=500px>
</p>

## Notes on the Solution

In the following, the methods and decisions followed for each step are described, as well as the major results. Note that the output files are in the folder [`results`](results).

### Step 1: Resample, Crop and Persist Rasters

Even though *resampling* to the minimum available resolution (60m) is not necessary, it facilitates many subsequent steps, since all pixelmaps have the same standardized size. That comes with the cost of losing resolution. Additionally, it should be considered that the ultimate maps required to extract the lake polygons (NDVI and NDWI) are computed with bands that share the same resolution, which is larger than the minimum one.

Note that in the package/scripts, the resampling can be easily switched off.

Once the bands are resampled, it is possible to stack them and to work with all of them together. Cropping is easily achieved with rasterio.

Actions implemented to achieve step 1:

- Implementation of the function `resample_persist_band()`: given a band path, it resamples and stores it to disk.
- Resample and save all bands.
- Implementation of the function `crop_persist_band()`: given a band path, it crops and stores it to disk.
- Crop and save all bands.
- Function `load_band_image()`: given a band path, load it and resample it if desired.
- Load all cropped bands.
- Plot cropped, saved bands.
- Plot band histograms and their characteristics (mean & std).

Whenever possible, I have already modularized the code into functions, to ease the transfer of the notebook to a production environment.

Scene 1 - ROI and points:

![Scene 1: ROI and points](./assets/scene_1_geom.jpg)

Scene 1 - Cropped band and points:

![Scene 1: Cropped band and points](./assets/scene_1_geom_crop.jpg)

Scene 2 - ROI and points:

![Scene 2: ROI and points](./assets/scene_2_geom.jpg)

Scene 2 - Cropped band and points:

![Scene 2: Cropped band and points](./assets/scene_2_geom_crop.jpg)

### Step 2: Compute the NDVI and the NDWI Maps

The computation of the NDVI ([Normalized Difference Vegetation Index](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index)) and the NDWI ([Normalized Difference Water Index](https://en.wikipedia.org/wiki/Normalized_difference_water_index)) is well defined:

    NDVI = (NIR - Red) / (NIR + Red) = (B8 - B4) / (B8 + B4)
    NDWI = (Green - NIR) / (Green + NIR) = (B3 - B8) / (B3 + B8)

In case we didn't have the Green band (B3) necessary to compute the NDWI we could use a shortwave infrared (SWIR) band (i.e., B11 or B12) and the near infrared band (B8 or B8A):

    NDWI = (NIR - SWIR) / (NIR + SWIR) (approx.)
    NDWI = (B8A - B12) / (B8A + B12) (approx.)
    NDWI = (B8A - B11) / (B8A + B11) (approx.)

However, that is not necessary in with the analyzed scenes.

Steps implemented to achieve step 2:

- Implementation of the function `compute_ndvi()`: given band arrays, compute the NDVI map.
- Function `compute_ndwi()`: given band arrays, compute the NDWI map.
- Function `generate_persist_ndmap()`: given band arrays, compute either the NDVI or NDWI map and save it to disk.
- Compute and persist the NDVI and NDWI maps for the scene.
- Load the NDVI and NDWI maps and visualize them.

Scene 1 - NDVI:

![Scene 1: NDVI](./assets/scene_1_ndvi.jpg)

Scene 1 - NDWI:

![Scene 1: NDWI](./assets/scene_1_ndwi.jpg)

Scene 2 - NDVI:

![Scene 2: NDVI](./assets/scene_2_ndvi.jpg)

Scene 2 - NDWI:

![Scene 2: NDWI](./assets/scene_2_ndwi.jpg)

### Step 3: Extract Water Shapes

In a regular situation, the NDWI map should be used to detect water bodies: pixels with an index value that passes a known threshold are expected to be water pixels; however, the NDWI map of Scene 2 is not as homogeneous as expected.

In case the NDWI or the relevant bands have a low quality, other approaches are worth trying to extract water bodies:

- [Modified NDWI]((https://www.tandfonline.com/doi/abs/10.1080/01431160600589179?journalCode=tres20)): `(Green - SWIR)/(Green + SWIR)`; however, we lack of the `Green` band.
- [Tasseled cap transformation](https://en.wikipedia.org/wiki/Tasseled_cap_transformation): the bands are transformed to a lower dimensional eigen-space using Principal Component Analysis (PCA) that might help detecting bright, green or wet bodies.
- Create a pixel-wise classification model (i.e., semantic segmentation) which is trained on labeled data. Letting a supervised machine learning model automatically detect patterns on hyperspectral/multi-band images has been proven to be effective in recent years. The issue with this approach: we need annotated data; we could use Scene 1, but, probably, the bands should be calibrated so that the pixel values represent the same physics behind them.

All in all, the following tasks are carried out to extract water shapes:

- Load the saved NDVI or NDWI maps; each scene uses a different one.
- Perform thresholding on the map to obtain a mask of the candidate water bodies.
- Convert the water body BLOBs into polygons of a GeoSeries.
- Plot the mask and the polygons.

Scene 1 - Water body polygons:

![Scene 1: Water body polygons](./assets/scene_1_water_bodies.jpg)

Scene 2 - Water body polygons:

![Scene 2: Water body polygons](./assets/scene_2_water_bodies.jpg)

### Step 4: Identify Lake Polygons

After accomplishing the previous step, we have a series of polygons that represent candidate water bodies; now, the goal is to select the polygons which contain or are closest to the target points provided in the challenge. Then, the filtered polygons are tagged with the point id.

Scene 1 yields good results; in contrast, the lakes in Scene 2 are incomplete.

The following steps are taken to id the polygons:

- Filter the water body polygons: take the ones which contain or are closest to the target points using built-in `contains()` and `distance()` methods from GeoPandas.
- Assemble GeoDataFrame and save it to disk as a GeoJSON.
- Plot the final result: masked raster + select water polygons + original target points

Scene 1 - Identified lake polygons:

![Scene 1: Identified lake polygons](./assets/scene_1_lake_polygons.png)

Scene 2 - Identified lake polygons:

![Scene 2: Identified lake polygons](./assets/scene_2_lake_polygons.png)

### Production Environment

The production code is organized as follows:

- A library/package [`geo_toolkit`](geo_toolkit) which contains generic and reusable functions in [`geo_toolkit/geo_library.py`](geo_toolkit/geo_library.py).
- A python script [`vectorize_water_blobs.py`](vectorize_water_blobs.py) which uses the library and has code with fine-tuned parameters.

Since the code in the notebook was modularized, creating a package/library was easy. In addition to the functions in the notebooks, I have created these new ones:

- `resample_bands()`
- `crop_bands()`
- `load_bands()`

The production code is PEP8-conform (linted) and uses logging as well as exception handling.

Finally, testing was added using Pytest in the folder [`tests`](tests); to use it:

```bash
pytest tests
```

Currently, only one function is tested; of course, in a regular environment, all functions should be tested.

### Summary and Conclusions

In the following, I provide a list of the submitted deliverables, both required and non-required contributions.

Accomplished main steps:

- [x] Cropped bands (scenes 1 & 2).
- [x] Computed NDVI and NDWI index maps (scenes 1 & 2).
- [x] Extracted water body shapes (scene 1; results for scene 2 are not that promising)
- [x] Processed the water body shapes according to the GeoJSON (scenes 1 & 2; the polygons for scene 2 are not correct because the input blobs are not good).

Additional contributions:

- [x] Documented project.
  - [x] Interpretation.
  - [x] Decisions: methods, tools.
- [x] Python package: PEP8-conform, linted.
- [x] Testing with Pytest.
- [x] Logging.

## Limitations, Improvements

- Persisting images in different stages: not really necessary?
- Try histogram equalization for band 10?
- Resampling: make it clearly optional.
- NDWI of scene 2: it has lesser quality but still seems usable. Try other approaches to detect water bodies in scene 2; see for instance [space_exploration](https://github.com/mxagar/space_exploration).
  - Tasseled cap transformation.
  - Create a pixel-wise classification model based on the data in scene 1.
- Refactor: functions one-task only, OOP, SOLID principles, etc.
- Configuration file for the production environment, similar to [`config_test.yaml`](./config_test.yaml)
- Flask web app; see for instance [disaster_response_pipeline](https://github.com/mxagar/disaster_response_pipeline).
- Containerization; see for instance [census_model_deployment_fastapi](https://github.com/mxagar/census_model_deployment_fastapi).

## References, Links and Assets

General links/assets:

- [chrieke/awesome-geospatial-companies](https://github.com/chrieke/awesome-geospatial-companies)
- [How to Download Free Sentinel Satellite Data](https://gisgeography.com/how-to-download-sentinel-satellite-data/)

Resources:

- My notes on how to process satellite images and geo-spatial data: [space_exploration](https://github.com/mxagar/space_exploration)
- [Rasterio documentation](https://rasterio.readthedocs.io/en/stable/)
- [EarthPy documentation](https://earthpy.readthedocs.io/en/latest/index.html)
- [Sentinel 2 bands](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/resolutions/spectral)
- [`resample_raster.py`](https://gist.github.com/lpinner/13244b5c589cda4fbdfa89b30a44005b)
- [Sentinel 2 Bands and Combinations](https://gisgeography.com/sentinel-2-bands-combinations/)
- Some toy tests/examples with geospatial datasets: [space_exploration](https://github.com/mxagar/space_exploration)

Literature:

- [Xu et al., 2007. *Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery*](https://www.tandfonline.com/doi/abs/10.1080/01431160600589179?journalCode=tres20)


## Terms of Use, Authorship and License

All the software files in this work except [`resample_raster.py`](utils/resample_raster.py) are protected by the GPL-v3.0 license; see [`LICENSE.md`](LICENSE.md) for more information. The file [`resample_raster.py`](utils/resample_raster.py) is protected by the [Apache License v2.0 license](http://www.apache.org/licenses/LICENSE-2.0).

Mikel Sagardia, 2023.  
[https://mikelsagardia.io](https://mikelsagardia.io)
