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


@staticmethod
def scatter_pe(plotting_configuration: PlottingConfiguration) -> None:
    exploration_data: util.ExplorationData = util.get_data_fully(plotting_configuration.input)

    counter: int = 0
    for method in exploration_data:

        # clear 
        plt.clf()

        # seaborn
        # plt.style.use('seaborn-v0_8-darkgrid')

        # assemble plot
        plt.title(plotting_configuration.name + " - Scatter", fontsize=plotting_configuration.fontsize) # type: ignore
        plt.xlabel("Samples") # type: ignore
        plt.ylabel("Log Runtime (ms)") # type: ignore


        for run in exploration_data[method][1]:

            y: List[float] = []

            maximum: float = max([float(elem['runtime']) for elem in exploration_data[method][1][run]])

            for line in exploration_data[method][1][run]:

                if float(line['runtime']) < 0:
                    y.append(np.log10(maximum * 1.01))
                else:
                    y.append(np.log10(float(line['runtime'])))

            x: List[float] = list(range(len(y)))

            # add line for performance evolution
            pe: List[float] = []

            # init minimum with first valid value found 
            minimum: float = 0
            for line in exploration_data[method][1][run]:
                if(float(line['runtime']) > 0):
                    minimum = float(line['runtime'])
                    break
                    
            # create performance evolution 
            # new entry everytime we find a new minimum value 
            for line in exploration_data[method][1][run]:
                if float(line['runtime']) > 0:
                    if float(line['runtime']) < minimum:
                        minimum = float(line['runtime'])
                pe.append(np.log10(minimum))

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
        log_appendix:str = ""
        if plotting_configuration.log:
            log_appendix = "_log"

        plt.savefig( # type: ignore
            f"{plotting_configuration.output}/{plotting_configuration.name}_scatter_pe_{method}{log_appendix}.{plotting_configuration.format}",
            dpi=plotting_configuration.dpi)

    return None