#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

from . import util

import plotly.graph_objects as go

import numpy as np


def scatter(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration)

    y = []
    for method in data:
        for run in data[method][1]:

            maximum = max([float(elem['runtime']) for elem in data[method][1][run]])

            for line in data[method][1][run]:

                if float(line['runtime']) < 0:
                    y.append(np.log10(maximum * 1.01))
                else:
                    y.append(np.log10(float(line['runtime'])))

    x = list(range(len(y)))

    # Create trace for scatter plot
    trace = go.Scatter(x=x, y=y, mode='markers', marker=dict(size=1))

    # Create layout for the plot
    layout = go.Layout(title='Simple Scatter Plot',
                       xaxis=dict(title='X-axis'),
                       yaxis=dict(title='Y-axis'))

    # Create figure and add trace and layout
    fig = go.Figure(data=trace, layout=layout)

    # Show the figure
    fig.show()

    return None
