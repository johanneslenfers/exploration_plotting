#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

from . import util

import plotly.graph_objects as go

import numpy as np


def scatter(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration)

    for method in data:

        layout = go.Layout(title=f'Scatter Plot - {method}',
                           xaxis=dict(title='Samples'),
                           yaxis=dict(title='Log Runtime (ms)'))

        y = []
        print(f"method: {method}")
        for run in data[method][1]:

            maximum = max([float(elem['runtime']) for elem in data[method][1][run]])

            for line in data[method][1][run]:

                if float(line['runtime']) < 0:
                    y.append(np.log10(maximum * 1.01))
                else:
                    y.append(np.log10(float(line['runtime'])))

        x = list(range(len(y)))

        trace = go.Scatter(x=x, y=y, mode='markers', marker=dict(size=0.5, color='black'))

        fig = go.Figure(data=trace, layout=layout)

        fig.write_image(
            f"{plotting_configuration.output}/{plotting_configuration.name}_{method}_scatter.{plotting_configuration.format}")

    return None
