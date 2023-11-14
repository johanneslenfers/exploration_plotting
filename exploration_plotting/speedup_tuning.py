#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

import plotly.graph_objects as go

from . import util


def speedup_tuning(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration)

    for method in data:
        print(f"method: {method}")
        for run in data[method][1]:
            grouped_by_tuning = util.group_by_tuning(data[method][1][run])

            fig = go.Figure()

            group_conter = 0
            for group in grouped_by_tuning:
                # process group
                # add line to plot
                pe = []

                minimum = float(group[0]['runtime'])

                for elem in group:
                    if elem['error-level'] == 'None':
                        if float(elem['runtime']) < minimum:
                            minimum = float(elem['runtime'])

                    pe.append(minimum)

                group_conter += 1

                x = list(range(len(group)))

                min = pe[0]
                y = [min / elem for elem in pe]

                fig.add_trace(go.Scatter(x=x, y=y))

            fig.show()

    return None
