# Open Cosmos Challenge

This is the challenge from Open Cosmos for the Data Scientist role.


More information:

- [Challenge Instructions](./Data%20Scientist%20-%20Challenge%20Project.pdf)



Intro.

<p style="text-align:center">
  <img src="./assets/word_cloud.png" alt="A wordcloud." width=1000px>
</p>

Questions:

1. A
2. B
3. C

## Table of Contents

- [Open Cosmos Challenge](#open-cosmos-challenge)
  - [Table of Contents](#table-of-contents)
  - [How to Use This Project](#how-to-use-this-project)
    - [Installing Dependencies for Custom Environments](#installing-dependencies-for-custom-environments)
  - [Dataset](#dataset)
  - [Notes on the Implemented Analysis](#notes-on-the-implemented-analysis)
    - [Summary of Contents](#summary-of-contents)
  - [Results and Conclusions](#results-and-conclusions)
  - [Next Steps, Improvements](#next-steps-improvements)
  - [References and Links](#references-and-links)
  - [Authorship and Terms of Use](#authorship-and-terms-of-use)

## How to Use This Project

The directory of the project consists of the following files:

```
.
├── Instructions.md           # Original challenge instructions
...
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
conda activate env-name
# Or
conda create --name env-name pip
conda install <package>

# Install pip dependencies
pip install requirements.txt

# Track any changes and versions you have
conda env export > conda_.yaml
pip list --format=freeze > requirements_.txt
```

List of most important dependencies:

- A
- B

## Dataset

## Notes on the Implemented Analysis

### Summary of Contents

- [ ] A
- [ ] B

## Results and Conclusions

## Next Steps, Improvements

## References and Links

General links/assets related to the job opening:

- [Open Cosmos](https://www.open-cosmos.com/)
- [Open Cosmos: Data Scientist (Job Opening)](./assets/OpenCosmos_DataScientist_JobOpening.pdf)

Interesting resources:

- [space_exploration](https://github.com/mxagar/space_exploration)
- [Sentinel 2 bands](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/resolutions/spectral)
- [Supported raster formats](https://gdal.org/drivers/raster/index.html)
- [Supported vector formats](https://gdal.org/drivers/vector/)

## Authorship and Terms of Use

Mikel Sagardia, 2023.  
No guarantees.


