#!/bin/python3.10
from __future__ import annotations

from typing import (
    List,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

import util

from matplotlib import pyplot as plt

import numpy as np

# seaborn
plt.style.use('seaborn-v0_8-darkgrid')


@staticmethod
def scatter_pe(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration.input)

    # assemble plot
    plt.title(plotting_configuration.name + " - Scatter", fontsize=plotting_configuration.fontsize) # type: ignore
    plt.xlabel("Samples") # type: ignore
    plt.ylabel("Log Runtime (ms)") # type: ignore

    counter: int = 0
    for method in data:

        for run in data[method][1]:

            y: List[float] = []
            x: List[float] = []

            maximum = max([float(elem['runtime']) for elem in data[method][1][run]])

            for line in data[method][1][run]:

                if float(line['runtime']) < 0:
                    y.append(np.log10(maximum * 1.01))
                else:
                    y.append(np.log10(float(line['runtime'])))

            x = list(range(len(y)))

            # add line for performance evolution
            pe: List[float] = []
            min = 30000000
            for line in data[method][1][run]:
                if float(line['runtime']) > 0:
                    if float(line['runtime']) < min:
                        min = float(line['runtime'])
                pe.append(np.log10(min))

            # plot
            plt.plot(x, # type: ignore
                     pe, 
                     alpha=0.9, 
                     color=util.colors[counter % len(util.colors)], 
                     lw=0.5, 
                     label=run
                     ) 
            plt.scatter(x, # type: ignore
                        y, 
                        alpha=0.9, 
                        color=util.colors[counter % len(util.colors)], 
                        label=run, 
                        lw=0.2, 
                        s=0.2
                        )
            counter += 1

    # add legend
    # plt.legend()
    # change size of points?

    # save to file
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}{log_appendix}.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)

    return None