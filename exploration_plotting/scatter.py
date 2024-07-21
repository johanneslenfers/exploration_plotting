#!/bin/python3.10
from __future__ import annotations

import util

import plotly.graph_objects as go # type: ignore

import numpy as np

from typing import (
    List,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

@staticmethod
def scatter(plotting_configuration: PlottingConfiguration) -> None:
    data: util.ExplorationData = util.get_data_fully(plotting_configuration.input)

    for method in data:

        layout: go.Layout = go.Layout(title=f'Scatter Plot - {method}',
                           xaxis=dict(title='Samples'),
                           yaxis=dict(title='Log Runtime (ms)'))

        y: List[float] = []
        print(f"method: {method}")
        for run in data[method][1]:

            maximum: float = max([float(elem['runtime']) for elem in data[method][1][run]])

            for line in data[method][1][run]:

                if float(line['runtime']) < 0:
                    y.append(np.log10(maximum * 1.01))
                else:
                    y.append(np.log10(float(line['runtime'])))

        x: List[int] = list(range(len(y)))

        trace: go.Scatter = go.Scatter(x=x, y=y, mode='markers', marker=dict(size=0.5, color='black'))

        fig: go.Figure = go.Figure(data=trace, layout=layout)

        fig.write_image( # type: ignore
            f"{plotting_configuration.output}/{plotting_configuration.name}_{method}_scatter.{plotting_configuration.format}")

    return None
