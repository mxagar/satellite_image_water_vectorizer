# Open Cosmos Challenge

This my solution to the challenge from Open Cosmos for the role *Data Scientist*, published in February 2023.

Synopsis - [challenge instructions](./Data_Scientist_Challenge_Project.pdf).

<p style="text-align:center">
  <img src="./assets/word_cloud.png" alt="A wordcloud." width=1000px>
</p>

Tasks:

1. A
2. B
3. C
4. D

## Table of Contents

- [Open Cosmos Challenge](#open-cosmos-challenge)
  - [Table of Contents](#table-of-contents)
  - [How to Use This Project](#how-to-use-this-project)
    - [Installing Dependencies for Custom Environments](#installing-dependencies-for-custom-environments)
  - [Dataset](#dataset)
  - [Notes on the Implemented Analysis](#notes-on-the-implemented-analysis)
    - [Summary and Conclusions](#summary-and-conclusions)
  - [Next Steps, Improvements](#next-steps-improvements)
  - [References, Links and Assets](#references-links-and-assets)
  - [Authorship and Terms of Use](#authorship-and-terms-of-use)

## User Guide

The directory of the project consists of the following files:

```
.
├── Data_Scientist_Challenge_Project.pdf
├── Dockerfile
├── LICENSE.md
├── README.md
├── app
├── assets
│   └── OpenCosmos_DataScientist_JobOpening.pdf
├── data
│   ├── Scene 1 ...
│   │   ├── B01_COG.tiff
│   │   ├── ...
│   │   ├── B12_COG.tiff
│   │   └── lakes.geojson
│   └── Scene 2 ...
│       ├── B01_COG.tiff
│       ├── ...
│       ├── B12_COG.tiff
│       └── lakes.geojson
├── docker-compose.yaml
├── geo_vectorizer
├── notebooks
├── requirements.txt
├── conda.yaml
├── tests
│   └── conftest.py
└── vectorize_water_blobs.py
```

You can run the notebook at leas in two ways:

1. In a custom environment, e.g., locally or on a container. To that end, you can create a [conda](https://docs.conda.io/en/latest/) environment and install the [dependencies](#installing-dependencies-for-custom-environments) as explained below.
2. In Google Colab. For that, simply click on the following link:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mxagar/airbnb_data_analysis/blob/master/00_AirBnB_DataAnalysis_Initial_Tests.ipynb)


### Installing Dependencies for Custom Environments

If you'd like to control where the notebook runs, you need to create a custom environment and install the required dependencies. A quick recipe which sets everything up with [conda](https://docs.conda.io/en/latest/) is the following:

```bash
# Create environment with YAML, incl. packages
conda env create -f conda.yaml
conda activate cosmos
# Or
conda create --name cosmos pip python=3.10
pip install -r requirements.txt

# Track any changes and/or versions
conda env export > conda.yaml
pip list --format=freeze > requirements.txt
```

List of most important dependencies:

- A
- B

## Dataset and Task

## Notes on the Solution

### Summary and Conclusions

In the following, I provide a list of the submitted deliverables, both required and non-required contributions.

Accomplished main objectives:

- [ ] Cropped image.
- [ ] Computed NDVI and NDWI.
- [ ] Extracted water body shapes.
- [ ] Processed the water body shapes according to the GeoJSON.

Additional, required:

- [ ] Documented project.
  - [ ] Interpretation (reasoning).
  - [ ] Decisions: methods, tools (reasoning).
- [ ] Slides.

Extra contributions, non-required:

- [ ] Python package.
- [ ] Testing.
- [ ] Logging.
- [ ] Flask web app.
- [ ] Containerization.

All in all, 

## Next Steps, Improvements

## References, Links and Assets

General links/assets related to the job opening:

- [Open Cosmos](https://www.open-cosmos.com/)
- [Open Cosmos: Data Scientist (Job Opening)](./assets/OpenCosmos_DataScientist_JobOpening.pdf)

Resources:

- [space_exploration](https://github.com/mxagar/space_exploration)
- [Sentinel 2 bands](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/resolutions/spectral)
- [Supported raster formats](https://gdal.org/drivers/raster/index.html)
- [Supported vector formats](https://gdal.org/drivers/vector/)

## Terms of Use, Authorship and License

As stated in the instructions

> [...] The rights to the images remain with the original holder and you must delete them when the project is completed.

The software files in this work are protected by the GPL-v3.0 license; see [`LICENSE.md`](LICENSE.md) for more information.

Mikel Sagardia, 2023.  
