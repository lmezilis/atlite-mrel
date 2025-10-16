# SPDX-FileCopyrightText: Contributors to atlite <https://github.com/pypsa/atlite>
#
# SPDX-License-Identifier: MIT

"""
atlite datasets.
"""

from atlite.datasets import era5, gebco, sarah, cerra, mrel_wave

modules = {
    "era5": era5, 
    "sarah": sarah, 
    "mrel_wave": mrel_wave, 
    "cerra": cerra, 
    "gebco": gebco, 
    }
