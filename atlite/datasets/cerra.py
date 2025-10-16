
"""
In order to create a CERRA cutout, the data must be manually downloaded from the Climate Data Store.
The variable used is "10m wind speed" and there is not a direction component in it.
This 10m wind speed was transformed into a 100m wind speed in order to follow the rest of atlite's processes. 
"""

import xarray as xr
import numpy as np

import logging
from rasterio.warp import Resampling
from atlite.gis import regrid

logger = logging.getLogger(__name__)

crs = 4326 
dx = 0.05
dy = 0.05

features = {
    "wind": ["wnd100m", "roughness"]
    }

def as_slice(bounds, pad=True):
    """
    Convert coordinate bounds to slice and pad by 0.01.
    """
    if not isinstance(bounds, slice):
        bounds = bounds + (-0.01, 0.01)
        bounds = slice(*bounds)
    return bounds

def get_data(cutout, feature, tmpdir, **creation_parameters):
    """
    Retrieve data from a local CERRA dataset and process it.
    """
    coords = cutout.coords

    if "data_path" not in creation_parameters:
        logger.error('Argument "data_path" not defined')
        raise ValueError('Argument "data_path" not defined')
    path = creation_parameters["data_path"]

    ds = xr.open_dataset(path)

    ds = ds.sel(x=as_slice(cutout.extent[:2]), y=as_slice(cutout.extent[2:]))
    ds = ds.assign_coords(
        x=ds.x.astype(float).round(4), y=ds.y.astype(float).round(4)
    )

    if (cutout.dx != dx) or (cutout.dy != dy):
        ds = regrid(ds, coords["x"], coords["y"], resampling=Resampling.average)
    
    if 'sr' in ds:
        ds = ds.rename({"sr": "roughness"})

    logger.info("Calculating 100 metre wind speed")
    if 'si10' in ds and 'roughness' in ds:
        ds["wnd100m"] = (ds["si10"] * (np.log(100 / ds["roughness"]) / np.log(10 / ds["roughness"]))).assign_attrs(
            units="m s**-1", long_name="100 metre wind speed")
        ds = ds.drop_vars("si10")

    ds = ds.assign_coords(x=ds.coords["x"], y=ds.coords["y"])

    logger.info("Resampling to 1H.")
    ds = ds.resample(time='1h').interpolate("linear")

    return ds
