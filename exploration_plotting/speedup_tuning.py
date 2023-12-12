#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

import plotly.graph_objects as go
import numpy as np

from . import util


def speedup_tuning(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration)

    speedup_tuning_overlapped(data, plotting_configuration)
    max_speedup(data, plotting_configuration)

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
