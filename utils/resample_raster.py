# Copyright 2019 Luke Pinner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import contextmanager

import rasterio
from rasterio import Affine, MemoryFile
from rasterio.enums import Resampling


def resample_res(dataset, xres, yres, resampling=Resampling.bilinear):
    scale_factor_x = dataset.res[0]/xres
    scale_factor_y = dataset.res[1]/yres

    profile = dataset.profile.copy()
    # resample data to target shape
    data = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset.height * scale_factor_y),
            int(dataset.width * scale_factor_x)
        ),
        resampling=resampling
    )

    # scale image transform
    transform = dataset.transform * dataset.transform.scale(
        (1 / scale_factor_x),
        (1 / scale_factor_y)
    )
    profile.update({"height": data.shape[-2],
                    "width": data.shape[-1],
                   "transform": transform})

    return data, profile


def resample_scale(dataset, scale, resampling=Resampling.bilinear):
    """ Resample a raster
        multiply the pixel size by the scale factor
        divide the dimensions by the scale factor
        i.e
        given a pixel size of 250m, dimensions of (1024, 1024) and a scale of 2,
        the resampled raster would have an output pixel size of 500m and dimensions of (512, 512)
        given a pixel size of 250m, dimensions of (1024, 1024) and a scale of 0.5,
        the resampled raster would have an output pixel size of 125m and dimensions of (2048, 2048)
        returns a DatasetReader instance from either a filesystem raster or MemoryFile (if out_path is None)
    """
    # rescale the metadata
    # scale image transform
    t = dataset.transform
    transform = t * t.scale((scale), (scale))
    height = int(dataset.height / scale)
    width = int(dataset.width / scale)

    profile = dataset.profile.copy()
    profile.update(transform=transform, driver='GTiff', height=height, width=width)

    data = dataset.read(
            out_shape=(dataset.count, height, width),
            resampling=resampling,
        )

    return data, profile


@contextmanager
def write_mem_raster(data, **profile):
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dataset:  # Open as DatasetWriter
            dataset.write(data)

        with memfile.open() as dataset:  # Reopen as DatasetReader
            yield dataset  # Note yield not return


@contextmanager
def write_raster(path, data, **profile):

    with rasterio.open(path, 'w', **profile) as dataset:  # Open as DatasetWriter
        dataset.write(data)

    with rasterio.open(path) as dataset:  # Reopen as DatasetReader
        yield dataset


if __name__ == "__main__":

    xres, yres = 12.5, 12.5
    scale = 1.25

    input = "test.tif"
    output_res = "output_res.tif"
    output_scale = "output_scale.tif"

    with rasterio.open(input) as dataset:
        data_res, profile_res = resample_res(dataset, xres, yres)
        data_scale, profile_scale = resample_scale(dataset, scale)

    with rasterio.open(output_res, "w", **profile_res) as dataset:
        dataset.write(data_res)

    with rasterio.open(output_scale, "w", **profile_scale) as dataset:
        dataset.write(data_scale)