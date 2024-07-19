#!/bin/python3.10
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

import util

from matplotlib import pyplot as plt
import numpy as np

@staticmethod
def violin(plotting_configuration: PlottingConfiguration) -> None:

    exploration_data: util.ExplorationDataRuntime = util.get_data(plotting_configuration.input)
    violin_full(exploration_data=exploration_data, 
                plotting_configuration=plotting_configuration
                )


# TODO add type annotations
@staticmethod
def violin_full(exploration_data: util.ExplorationDataRuntime, plotting_configuration: PlottingConfiguration) -> None:
    violin_data = {}
    for method in exploration_data:

        violin_data[method] = []

        for run in exploration_data[method][1]:

            # convert to speedup and filter out failed ones
            runtimes_as_speedup = [plotting_configuration.default / elem[1] for elem in
                                   exploration_data[method][1][run] if elem[0] is True]

            # process log scale
            if plotting_configuration.log:
                runtimes_as_speedup = [np.log10(elem) for elem in runtimes_as_speedup]

            violin_data[method].append(runtimes_as_speedup)

    # violin plot for each method
    # overlapping runs of each method
    counter = 0
    for method in violin_data:
        counter += 1
        for run in violin_data[method]:
            plt.violinplot(run, positions=[counter], widths=1, showmeans=False)

    # set title and lables
    plt.xticks(range(1, len(violin_data) + 1), violin_data.keys()) # type: ignore
    plt.title('Speedup Violin Plot') # type: ignore
    if plotting_configuration.log:
        plt.ylabel('Speedup over Baseline (Log10)') # type: ignore
    else:
        plt.ylabel('Speedup over Baseline') # type: ignore

    # save figure
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}_violin_speedup{log_appendix}.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)
