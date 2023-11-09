#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import sem

from . import util

# seaborn
# warning, depreceated for python > python3.8
plt.style.use('seaborn')

# set global colors
colors = (
    "tab:red",
    "tab:green",
    "tab:cyan",
    "tab:olive",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:blue",
    "tab:orange",
    "tab:gray",
)


def performance_evolution(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data(plotting_configuration)

    performance_evolution_methods(plotting_configuration, data)

    return None


def performance_evolution_methods(plotting_configuration: PlottingConfiguration, data):
    plt.figure(figsize=plotting_configuration.figsize, dpi=plotting_configuration.dpi)

    # plot performance evolution for each method
    # sort by method
    keys: list[str] = sorted(data.keys(), key=lambda key: data[key][0])
    counter: int = 0
    for key in keys:
        performance_evolution_method(plotting_configuration, key, data[key][1], colors[counter % len(colors)])
        counter += 1

    # assemble plot
    plt.title(plotting_configuration.name + " - Performance Evolution", fontsize=plotting_configuration.fontsize)
    plt.xlabel("Samples")
    plt.ylabel("Log Runtime (ms)")
    plt.legend()

    # plot expert and default
    if plotting_configuration.expert:

        if plotting_configuration.log:
            expert = np.log10(plotting_configuration.expert)
        else:
            expert = plotting_configuration.expert

        plt.axhline(y=expert, color='black', linestyle='-', label='Expert', alpha=0.5)

    if plotting_configuration.default:

        if plotting_configuration.log:
            default: float = np.log10(plotting_configuration.default)
        else:
            default: float = plotting_configuration.expert

        plt.axhline(y=default, color='black', linestyle='-', label='Default', alpha=0.5)

    # save to file
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig(f"{plotting_configuration.output}/{plotting_configuration.name}{log_appendix}.pdf",
                dpi=plotting_configuration.dpi)

    return None


def performance_evolution_method(plotting_configuration: PlottingConfiguration, method_key, method_data, color):
    data_internal = {}
    for key in method_data:
        internal = []
        for elem in method_data[key]:
            internal.append(elem[1])

        data_internal[key] = internal

    # convert to data to represent performance evolution
    for key in data_internal:
        pe = []
        minimum = data_internal[key][0]
        for elem in data_internal[key]:
            if elem < minimum:
                minimum = elem

            if plotting_configuration.log:
                pe.append(np.log10(minimum))
            else:
                pe.append(minimum)

        data_internal[key] = pe

    means = []
    means_preparation = []
    confidence = []

    # prepare
    counter = -1
    for key in data_internal:
        counter += 1
        means_preparation.append([])
        for elem in data_internal[key]:
            means_preparation[counter].append(elem)

    minElem = min(list(map(lambda x: len(x), means_preparation)))
    for i in range(minElem):
        means_internal = []
        means_internal2 = []
        for file in means_preparation:
            means_internal.append(file[i])
            means_internal2.append(file[i])

        means.append(np.median(np.array(means_internal)))
        confidence.append(sem(means_internal2) * 1.96)

    # why cutting here?
    # means = means[0:50000]

    # Plot
    x = range(len(means))

    # qx = means.index
    plt.plot(x, means, alpha=0.8, color=color, lw=2, label=method_key)

    lower = []
    upper = []
    for i in range(len(means)):
        lower.append(means[i] - confidence[i])
        upper.append(means[i] + confidence[i])

    # plt.fill_between(x, lower, upper, color="#3F5D7D")
    plt.fill_between(x, lower, upper, color=color, alpha=0.2)

    return None
