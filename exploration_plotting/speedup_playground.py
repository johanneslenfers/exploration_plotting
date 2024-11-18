#!/bin/python3.10

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration


import plotly.graph_objects as go
import numpy as np

from matplotlib import pyplot as plt
# from scipy.stats import sem

import util 

# seaborn
# plt.style.use('seaborn-v0_8-darkgrid')


def speedup(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration.input)

    speedup_total_std(data, plotting_configuration)
    # speedup_total_grouped_by_category(data, plotting_configuration)
    # speedup_total_grouped_by_method(data, plotting_configuration)

    return None


def speedup_after_std(data, plotting_configuration: PlottingConfiguration) -> None:
    pass


def speedup_total_std(data, plotting_configuration: PlottingConfiguration) -> None:
    # speedup total
    plt.clf()

    default = plotting_configuration.default
    methods_speedup = []
    methods_std = []
    for method in data:

        method_speedups = []
        for run in data[method][1]:
            minimum = min([float(elem) for elem in
                           list(
                               filter(lambda elem: float(elem) > -1,
                                      [elem['runtime'] for elem in data[method][1][run]]))])

            method_speedups.append(default / minimum)

        # process log
        if plotting_configuration.log:
            method_speedups = [np.log10(elem) for elem in method_speedups]

        median = np.median(method_speedups)
        std = np.std(method_speedups)
        methods_speedup.append(median)
        methods_std.append(std)

    methods = [method for method in data]

    ind = np.arange(len(methods))
    width = 0.5

    # Create a bar plot
    plt.bar(ind, methods_speedup, width, color='green')
    plt.errorbar(ind, methods_speedup, yerr=methods_std, fmt='none', ecolor='black', capsize=10, elinewidth=5,
                 alpha=0.5)

    # Add title and labels to the plot
    plt.legend()
    plt.xticks(ind, methods)
    plt.title('Speedup over Baseline total')
    plt.xlabel('Method')

    if plotting_configuration.log:
        plt.ylabel('Speedup Log')
    else:
        plt.ylabel('Speedup')

    # save to file
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig(
        f"{plotting_configuration.output}/{plotting_configuration.name}{log_appendix}_speedup.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)

    pass


def speedup_total_grouped_by_category(data, plotting_configuration: PlottingConfiguration) -> None:
    plt.clf()
    default = plotting_configuration.default

    categories = [
        '1000',
        '5000',
        '10000',
        '15000',
        'total'
    ]

    categories_values = {}
    for category in categories:

        method_values = []
        for method in data:

            limit = 0
            if category == 'total':
                limit = max([len(data[method][1][run]) for run in data[method][1]])
            else:
                limit = int(category)

            method_speedups = []

            for run in data[method][1]:
                minimum = min([float(elem) for elem in
                               list(
                                   filter(lambda elem: float(elem) > -1,
                                          [elem['runtime'] for elem in data[method][1][run][:limit]]))])

                method_speedups.append(default / minimum)

            # process log
            if plotting_configuration.log:
                method_speedups = [np.log10(elem) for elem in method_speedups]

            # sort
            median = np.median(method_speedups)

            # todo include std to in the plots
            std = np.std(method_speedups)

            # save random sampling median in this category
            method_values.append(median)

        categories_values[category] = method_values

    # methods
    methods = [method for method in data]

    # number of methods?
    number_of_groups = len(methods)

    # number of categories
    bars_per_group = len(methods)

    # Position of bars on x-axis
    ind = np.arange(bars_per_group)

    # Width of a bar
    # todo make this dynamically
    width = 0.15

    # Dynamically calculate the offset to center the group of bars
    offset = (width * number_of_groups) / 2

    i = 0

    # add bars for each category
    for category in categories_values:
        positions = ind - offset + (i * width)
        plt.bar(positions, categories_values[category], width, label=f'{category}')
        i += 1

    plt.title('Speedups over Baseline')
    plt.xlabel('After Samples')
    plt.ylabel('Speedup')

    # Set the position of the x ticks
    plt.xticks(ind, methods)
    plt.legend()

    # save to file
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig(
        f"{plotting_configuration.output}/{plotting_configuration.name}{log_appendix}_speedup_grouped.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)


def speedup_total_grouped_by_method(data, plotting_configuration: PlottingConfiguration) -> None:
    plt.clf()
    default = plotting_configuration.default

    categories = [
        '200',
        '400',
        '600',
        '800',
        '1000',
        '2000',
        '5000',
        '10000',
        'total'
    ]

    methods_values = {}
    for method in data:

        medians = []
        for category in categories:

            limit = 0
            if category == 'total':
                limit = max([len(data[method][1][run]) for run in data[method][1]])
            else:
                limit = int(category)

            method_speedups = []

            for run in data[method][1]:
                minimum = min([float(elem) for elem in
                               list(
                                   filter(lambda elem: float(elem) > -1,
                                          [elem['runtime'] for elem in data[method][1][run][:limit]]))])

                method_speedups.append(default / minimum)

            # process log
            if plotting_configuration.log:
                method_speedups = [np.log10(elem) for elem in method_speedups]

            # sort
            median = np.median(method_speedups)

            # todo include this into the plots
            std = np.std(method_speedups)

            # compute variance
            medians.append(median)

        methods_values[method] = medians

    number_of_groups = len(methods_values)
    bars_per_group = len(categories)

    # Position of bars on x-axis
    ind = np.arange(bars_per_group)

    # Width of a bar
    width = 0.15

    # Dynamically calculate the offset to center the group of bars
    offset = (width * number_of_groups) / 2

    i = 0
    for method in methods_values:
        # Compute each group's bar positions
        positions = ind - offset + (i * width)
        plt.bar(positions, methods_values[method], width, label=f'{method}')
        i += 1

    plt.title('Speedups over Baseline')
    plt.xlabel('After Samples')
    plt.ylabel('Speedup')

    # Set the position of the x ticks
    plt.xticks(ind, categories)
    plt.legend()

    # save to file
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig(
        f"{plotting_configuration.output}/{plotting_configuration.name}{log_appendix}_speedup_grouped_method.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)
