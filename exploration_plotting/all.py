#!/bin/python3.10
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration


from scatter import scatter
from scatter_pe import scatter_pe
from performance_evolution import performance_evolution
from speedup import speedup
from speedup_tuning import speedup_tuning
from violin import violin
from stats import stats


def all(plotting_configuration: PlottingConfiguration) -> None:
    scatter(plotting_configuration)
    scatter_pe(plotting_configuration)
    performance_evolution(plotting_configuration)
    stats(plotting_configuration)
    speedup(plotting_configuration)
    speedup_tuning(plotting_configuration)
    violin(plotting_configuration)
