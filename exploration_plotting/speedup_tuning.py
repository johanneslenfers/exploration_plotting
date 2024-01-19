#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

import plotly.graph_objects as go
import numpy as np

from . import util

from matplotlib import pyplot as plt

# from scipy.stats import sem

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


def speedup_tuning(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration)

    # speedup_tuning_overlapped(data, plotting_configuration)
    # max_speedup(data, plotting_configuration)
    speedup_tuning_average(data, plotting_configuration)

    return None


def speedup_tuning_average(data, plotting_configuration: PlottingConfiguration) -> None:
    # plot average speedup introduce by tuning as bar plot

    # plot this with until a certain number of configs is reached?
    # speedup total
    plt.clf()

    speedups_of_methods = {}
    std_of_methods = {}
    for method in data:
        speedups_of_method = []
        for run in data[method][1]:
            grouped_by_tuning = util.group_by_tuning(data[method][1][run])

            speedups_of_groups = []
            for group in grouped_by_tuning:

                # get minima
                minimum = float(group[0]['runtime'])
                for elem in group:
                    if elem['error-level'] == 'None':
                        if float(elem['runtime']) < minimum:
                            minimum = float(elem['runtime'])

                # minimum vs first element to compute speedup
                baseline = None
                for value in group:
                    if value['error-level'] == 'None':
                        baseline = float(value['runtime'])
                        break

                # check if baseline and minimum are valid
                if baseline is not None and minimum > -1:
                    speedups_of_groups.append(baseline / minimum)

            # process log
            if plotting_configuration.log:
                speedups_of_groups = [np.log10(elem) for elem in speedups_of_groups]

            # get average here
            speedups_of_method.append(np.average(speedups_of_groups))

        speedups_of_methods[method] = np.median(speedups_of_method)
        std_of_methods[method] = np.std(speedups_of_method)

    methods_speedup = [speedups_of_methods[elem] for elem in speedups_of_methods]
    methods_error = [std_of_methods[elem] for elem in std_of_methods]

    # maybe groups
    methods = [method for method in data]

    ind = np.arange(len(methods))
    width = 0.5

    # Create a bar plot
    plt.bar(ind, methods_speedup, width, color="#3498db")
    plt.errorbar(ind, methods_speedup, yerr=methods_error, fmt='none', ecolor='black', capsize=10, elinewidth=5,
                 alpha=0.5)

    # Add title and labels to the plot
    plt.legend()
    plt.xticks(ind, methods)
    plt.title('Average Speedup of Tuning (per Tuning run)')
    plt.xlabel('Method')

    if plotting_configuration.log:
        plt.ylabel('Speedup Log')
    else:
        plt.ylabel('Speedup')

    # save to file
    log_appendix = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig(f"{plotting_configuration.output}/{plotting_configuration.name}{log_appendix}_speedup_per_tuning.pdf",
                dpi=plotting_configuration.dpi)

    return None


def speedup_tuning_overlapped(data, plotting_configuration: PlottingConfiguration) -> None:
    for method in data:
        print(f"method: {method}")
        for run in data[method][1]:
            grouped_by_tuning = util.group_by_tuning(data[method][1][run])

            layout = go.Layout(
                showlegend=False
            )

            traces = []

            print(f"groups: {len(grouped_by_tuning)}")

            for group in grouped_by_tuning:
                # process group
                # add line to plot
                pe = []

                # get minima
                minimum = float(group[0]['runtime'])

                for elem in group:
                    if elem['error-level'] == 'None':
                        if float(elem['runtime']) < minimum:
                            minimum = float(elem['runtime'])

                    pe.append(minimum)

                x = list(range(len(group)))

                # get first value as baseline for speedup computation
                min = pe[0]

                # make speedup
                y = [min / elem for elem in pe]

                # process log
                if plotting_configuration.log:
                    y = [np.log10(elem) for elem in y]

                traces.append(go.Scatter(x=x, y=y, mode='lines', line=dict(width=0.25)))

            fig = go.Figure(data=traces, layout=layout)

            log_appendix = ""
            if plotting_configuration.log:
                log_appendix = "_log"

            fig.write_image(
                f"{plotting_configuration.output}/{plotting_configuration.name}_{method}_tuning_speedups{log_appendix}.pdf")
            fig.show()

    return None


def max_speedup(data, plotting_configuration: PlottingConfiguration) -> None:
    for method in data:
        print(f"method: {method}")
        for run in data[method][1]:
            grouped_by_tuning = util.group_by_tuning(data[method][1][run])

            layout = go.Layout(
                showlegend=False
            )

            traces = []
            maximum_speedup = []

            print(f"groups: {len(grouped_by_tuning)}")

            for group in grouped_by_tuning:
                # process group
                # add line to plot
                pe = []

                # get minima
                minimum = float(group[0]['runtime'])

                for elem in group:
                    if elem['error-level'] == 'None':
                        if float(elem['runtime']) < minimum:
                            minimum = float(elem['runtime'])

                    pe.append(minimum)

                x = list(range(len(group)))

                # get first value as baseline for speedup computation
                min = pe[0]

                # make speedup
                y = [min / elem for elem in pe]

                # process log
                if plotting_configuration.log:
                    y = [np.log10(elem) for elem in y]

                maximum_speedup.append(max(y))

            x = list(range(len(maximum_speedup)))
            traces.append(
                go.Scatter(
                    x=x,
                    y=maximum_speedup,
                    mode='markers',
                    marker=dict(
                        size=2,  # Set the size of the markers here
                        color='black',  # Optional: you can also set the color of the markers
                    )
                )
            )

            fig = go.Figure(data=traces, layout=layout)

            log_appendix = ""
            if plotting_configuration.log:
                log_appendix = "_log"

            fig.write_image(
                f"{plotting_configuration.output}/{plotting_configuration.name}_{method}_max_speedup{log_appendix}.pdf")
            fig.show()

    return None
