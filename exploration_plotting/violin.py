#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

from . import util

from matplotlib import pyplot as plt
import numpy as np


def violin(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data(plotting_configuration)
    violin_full(data, plotting_configuration)


def violin_full(data, plotting_configuration: PlottingConfiguration) -> None:
    violin_data = {}
    for method in data:
        violin_data[method] = []

        for run in data[method][1]:
            # convert to speedup and filter out failed ones
            runtimes_as_speedup = [plotting_configuration.default / elem[1] for elem in
                                   data[method][1][run] if elem[0] is True]

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
    plt.xticks(range(1, len(violin_data) + 1), violin_data.keys())
    plt.title('Speedup Violin Plot')
    if plotting_configuration.log:
        plt.ylabel('Speedup over Baseline (Log10)')
    else:
        plt.ylabel('Speedup over Baseline')

    # save figure
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig(
        f"{plotting_configuration.output}/{plotting_configuration.name}_violin_speedup{log_appendix}.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)
