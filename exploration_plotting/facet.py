#!/bin/python3.10
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

import util

import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import seaborn as sns
import matplotlib.pyplot as plt


def facet_plot(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration.input)

    # Create subplots with shared x-axis
    for method in data:
        print(f"method: {method}")
        for run in data[method][1]:
            # print(f"run: {run}")
            grouped_by_tuning = util.group_by_tuning(data[method][1][run])

            global_min = 2147483647
            global_max = 0

            # rows = int(len(grouped_by_tuning) / 10) + 1
            fig = make_subplots(rows=1, cols=len(grouped_by_tuning), shared_yaxes=True, shared_xaxes=True)

            group_conter = 0
            row = 1
            for group in grouped_by_tuning:

                # preprocess

                # convert to performance evolution
                pe = []

                minimum = float(group[0]['runtime'])

                for elem in group:
                    if elem['error-level'] == 'None':
                        if float(elem['runtime']) < minimum:
                            minimum = float(elem['runtime'])

                    if plotting_configuration.log:
                        pe.append(np.log10(minimum))
                    else:
                        pe.append(minimum)

                group_conter += 1
                # Add traces to the subplots
                x = list(range(len(group)))
                y = pe

                # if group_conter % 10 == 0:
                #     row += 1
                #
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines'), row=1, col=group_conter)

                # get max and min of pe
                if global_max < max(pe):
                    global_max = max(pe)
                if global_min > min(pe):
                    global_min = min(pe)

    # Update layout
    fig.update_layout(height=1000, width=2000,
                      showlegend=False,
                      title_text="Facet Plot",
                      # xaxis=dict(title="X-axis", range=[0, 10]),
                      yaxis=dict(title="Y-axis", range=[global_min - 1, global_max + 1])
                      )
    print(f"global_min: {global_min}")
    print(f"global_max: {global_max}")
    # Show the plot
    fig.show()

    return None


def facet_plot_dev(plottingConfiguration: PlottingConfiguration, data) -> None:
    # Create sample data
    x = [1, 2, 3, 4, 5]
    y1 = [1, 4, 9, 16, 25]
    y2 = [5, 10, 15, 20, 25]

    # Create subplots with shared x-axis
    fig = make_subplots(rows=1, cols=6, shared_xaxes=True)

    # Add traces to the subplots
    fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Line 1'), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Line 2'), row=1, col=2)
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Line 2'), row=1, col=3)
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Line 2'), row=1, col=4)
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Line 2'), row=1, col=5)
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Line 2'), row=1, col=6)

    # Update layout
    fig.update_layout(height=600, width=800,
                      title_text="Facet Plot",
                      xaxis=dict(title="X-axis"),
                      yaxis=dict(title="Y-axis"))

    # Show the plot
    fig.show()
    return None


def facet_plot_dev2() -> None:
    # Create sample data
    x = [1, 2, 3, 4, 5]
    y1 = [1, 4, 9, 16, 25]
    y2 = [5, 10, 15, 20, 25]

    # Create a grid of subplots
    fig, axes = plt.subplots(1, 8, figsize=(8, 6))

    # Plot data on the subplots
    sns.lineplot(x=x, y=y1, ax=axes[0])
    # axes[0].set_title('Line 1')
    # axes[0].set_xlabel('X-axis')
    # axes[0].set_ylabel('Y-axis')

    sns.lineplot(x=x, y=y2, ax=axes[1])
    # axes[1].set_title('Line 2')
    # axes[1].set_xlabel('X-axis')
    # axes[1].set_ylabel('Y-axis')

    sns.lineplot(x=x, y=y2, ax=axes[1])
    # axes[2].set_title('Line 2')
    # axes[2].set_xlabel('X-axis')
    # axes[2].set_ylabel('Y-axis')

    sns.lineplot(x=x, y=y2, ax=axes[1])
    # axes[3].set_title('Line 2')
    # axes[3].set_xlabel('X-axis')
    # axes[3].set_ylabel('Y-axis')

    # Adjust spacing between subplots
    plt.tight_layout()

    # Show the plot
    plt.show()
