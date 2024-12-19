#!/bin/python3.10
from __future__ import annotations

import util

import plotly.graph_objects as go # type: ignore
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

import numpy as np
from scipy.stats import sem # type: ignore

from typing import (
    List,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

plt.style.use('seaborn-v0_8-darkgrid')

@staticmethod
def order_ranges(plotting_configuration: PlottingConfiguration) -> None:

    experiment_data: util.ExperimentData = util.get_data(plotting_configuration.input)

    for benchmark in experiment_data:

        print(f"benchmark: {benchmark}")

        plt.clf()
        plt.figure( # type: ignore
            figsize=(20, 10),  
            dpi=plotting_configuration.dpi
        )
        
        # collect methods for this benchmark 
        methods: list[str] = list(experiment_data[benchmark][0].keys())

        # make grid based on amount of plots 
        fig, axes = plt.subplots(1, len(methods), figsize=(10*len(methods), 10))  # 2 rows, 3 column # type: ignore

        method_count: int = 0
        for method in methods:

            print(f"    method: {method}")

            axis: plt.Axes = axes.flat[method_count]  # type: ignore
            axis.set_title(f"method_{method}", fontweight="bold") # type: ignore
            axis.set_yscale('log') # type: ignore 
            axis.yaxis.set_major_formatter(FuncFormatter(util.log_formatter)) # type: ignore
            # TODO: set y-axis limits dynamically 

            order_count: int = -1

            orders_means: list[list[float]] = []

            for order in experiment_data[benchmark]:
                order_count += 1

                # collect runtimes and convert to performance evolution
                tuning_runs: List[List[float]] = []
                for tuning_run in order[method]:
                    tuning_run_runtimes: List[float] = []
                    minimum: float = tuning_run[0].runtime
                    for sample in tuning_run:
                        if sample.runtime < minimum:
                            minimum = sample.runtime
                        tuning_run_runtimes.append(minimum)
                    
                    tuning_runs.append(tuning_run_runtimes)

                # collect means and confidence intervals
                means: List[float] = [] 
                confidence: List[float] = []

                # be careful here -> will fail if not all runs have the same length
                for i in range(len(tuning_runs[0])):

                    # group all runs at position i 
                    runs_at_position: List[float] = [run[i] for run in tuning_runs]

                    # compute mean for all runs at position i
                    means.append(float(np.median(np.array(runs_at_position))))

                    # compute confidence interval  
                    confidence.append(sem(runs_at_position) * 1.96) 


                # TODO: use a better metric, not the last element 
                # sort all means by the last element 
                # plot best and worst in the same color 
                # fill between 
                orders_means.append(means)


            # sort runs for all oders by last element and take best and worst 
            min_run: list[float] = sorted(orders_means, key=lambda x: x[-1])[0]
            max_run: list[float] = sorted(orders_means, key=lambda x: x[-1])[-1]


            x = range(len(min_run))

            # plot means 
            axis.plot(x,  # type: ignore 
                min_run, 
                alpha=0.9, 
                color='black',
                lw=2, 
                label=f"min"
            )

            # plot means 
            axis.plot(x,  # type: ignore 
                max_run, 
                alpha=0.9, 
                color='black',
                lw=2, 
                label=f"max"
            )

            # # plot confidence interval
            # lower: List[float] = []
            # upper: List[float] = []
            # for i in range(len(means)):
            #     lower.append(means[i] - confidence[i])
            #     upper.append(means[i] + confidence[i])

            axis.fill_between(x,  # type: ignore 
                            min_run, 
                            max_run, 
                            color='black', 
                            alpha=0.8
                            ) 

            # axis.scatter(x[-1],  # type: ignore 
            #     means[-1], 
            #     alpha=0.9, 
            #     color='black', 
            #     marker='x',
            #     lw=2, 
            # )

            method_count += 1

        plt.legend() # type: ignore
        plt.tight_layout() # type: ignore

        plt.savefig( # type: ignore
            f"{plotting_configuration.output}/{plotting_configuration.name}_{benchmark}_orders.{plotting_configuration.format}",
            dpi=plotting_configuration.dpi
            )

    return None
