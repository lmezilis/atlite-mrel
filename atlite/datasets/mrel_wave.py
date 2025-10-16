

import xarray as xr
import numpy as np
import logging
from rasterio.warp import Resampling
from atlite.gis import regrid 

logger = logging.getLogger(__name__)

crs = 4326
dx = 0.0625
dy = 0.04

features = {
    "wave_height" : ["wave_height"],
    "wave_period" : ["wave_period"]
}

def _rename_and_clean_coords(ds):
    """
    Rename 'longitude' and 'latitude' columns to 'x' and 'y' and fix roundings.

    Optionally (add_lon_lat, default:True) preserves latitude and
    longitude columns as 'lat' and 'lon'.
    """
    ds = ds.rename({"longitude": "x", "latitude": "y"})

    ds = ds.assign_coords(
        x=np.round(ds.x.astype(float), 5), y=np.round(ds.y.astype(float), 5)
    )


    return ds


def get_data_wave_height(ds):

    ds = ds.rename({"hs": "wave_height"})
    ds["wave_height"] = ds["wave_height"].clip(min=0.0)

    return ds

def get_data_wave_period(ds):

    ds = ds.rename({"tp": "wave_period"})
    # ds["wave_period"] = (1 / ds["wave_period"])
    ds["wave_period"] = ds["wave_period"].clip(min=0.0)

    return ds

def as_slice(bounds, pad=True):
    """
    Convert coordinate bounds to slice and pad by 0.01.
    """
    if not isinstance(bounds, slice):
        bounds = bounds + (-0.01, 0.01)
        bounds = slice(*bounds)
    return bounds

def get_data(cutout, feature, tmpdir, **creation_parameters):

    coords = cutout.coords

    if "data_path" not in creation_parameters:
        logger.error('Argument "data_path" not defined')
        raise ValueError('Argument "data_path" not defined')
    path = creation_parameters["data_path"]

    ds = xr.open_dataset(path)

    if 'longitude' in ds and 'latitude' in ds:
        ds = ds.rename({"longitude": "x", "latitude": "y"})

    ds = ds.sel(x=as_slice(cutout.extent[:2]), y=as_slice(cutout.extent[2:]))
    ds = ds.assign_coords(
        x=ds.x.astype(float).round(4), y=ds.y.astype(float).round(4)
    )

    if (cutout.dx != dx) or (cutout.dy != dy):
        ds = regrid(ds, coords["x"], coords["y"], resampling=Resampling.average)
    

    # coords = cutout.coords

    # if "data_path" not in creation_parameters:
    #     logger.error('Argument "data_path" not defined')
    #     return None

    # path = creation_parameters["data_path"]

    # logger.info(f"Opening dataset from {path}")
    # ds = xr.open_dataset(path, chunks=cutout.chunks)
    # ds = _rename_and_clean_coords(ds)

    variables = ds.data_vars


    for var in variables:
        if var not in ['hs', 'tp']:
            ds = ds.drop_vars(var)



    # ds = ds.sel(x=as_slice(cutout.extent[:2]), y=as_slice(cutout.extent[2:]))

    # if (cutout.dx != dx) or (cutout.dy != dy):
    #     ds = regrid(ds, coords["x"], coords["y"], resampling=Resampling.average)

    logger.info("Obtaining wave data.")

    ds = get_data_wave_height(ds)
    ds = get_data_wave_period(ds)

    # ds = ds.assign_coords(x=ds.coords["x"], y=ds.coords["y"])

    return ds



