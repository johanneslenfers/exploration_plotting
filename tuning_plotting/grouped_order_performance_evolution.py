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
def grouped_order_performance_evolution(plotting_configuration: PlottingConfiguration) -> None:

    experiment_data: util.ExperimentData = util.get_data(plotting_configuration.input)


    for benchmark in experiment_data:
        print(f"benchmark: {benchmark}")

        plt.clf()
        plt.figure( # type: ignore
            figsize=(20, 15),  # is this ignored? do we overwrite?
            dpi=plotting_configuration.dpi
        )

        amount_of_orders: int = len(experiment_data[benchmark])

        rows: int = 0
        columns: int = 0
        if amount_of_orders <= 4:
            rows = 1
            columns = amount_of_orders
        else:
            if amount_of_orders % 4 == 0:
                rows = int(amount_of_orders / 4)
                columns = 4
            else:
                rows = int((amount_of_orders)/ 4) + 1
                columns = 4
        
        # make grid based on amount of plots 
        width: int = 20
        fig, axes = plt.subplots(rows, columns, figsize=(width, rows * (width/columns)))  # type: ignore

        # get global min 
        # get global max
        global_ranges: tuple[float, float] = get_global_range(experiment_data[benchmark])
        # add some space 
        global_ranges = (global_ranges[0] * 0.8, global_ranges[1] * 1.2) 

        order_count: int = 0
        for order in experiment_data[benchmark]:

            axis: plt.Axes = axes.flat[order_count]  # type: ignore
            axis.set_title(f"order_{order_count}", fontweight="bold") # type: ignore
            axis.set_yscale('log') # type: ignore 
            axis.yaxis.set_major_formatter(FuncFormatter(util.log_formatter)) # type: ignore
            # axis.legend() # type: ignore

            axis.set_ylim(bottom=global_ranges[0], top=global_ranges[1]) # type: ignore

            # create one line for each method in this plot  
            for method in order:

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

                # be careful here -> will fail if tuning runs have different length 
                for i in range(len(tuning_runs[0])):

                    # group all runs at position i 
                    runs_at_position: List[float] = [run[i] for run in tuning_runs]

                    # compute mean for all runs at position i
                    means.append(float(np.median(np.array(runs_at_position))))

                    # compute confidence interval  
                    confidence.append(sem(runs_at_position) * 1.96) 

                x = range(len(means))

                # plot means 
                axis.plot(x,  # type: ignore 
                    means, 
                    alpha=0.9, 
                    # color='black',
                    lw=2, 
                    label=method
                )

                # plot confidence interval
                lower: List[float] = []
                upper: List[float] = []
                for i in range(len(means)):
                    lower.append(means[i] - confidence[i])
                    upper.append(means[i] + confidence[i])

                axis.fill_between(x,  # type: ignore 
                                 lower, 
                                 upper, 
                                #  color='black', 
                                 alpha=0.2
                                 ) 

                # axis.scatter(x[-1],  # type: ignore 
                #     means[-1], 
                #     alpha=0.9, 
                #     color='black', 
                #     marker='x',
                #     lw=2, 
                # )

            order_count += 1

        plt.legend() # type: ignore
        plt.tight_layout() # type: ignore

        plt.savefig( # type: ignore
            f"{plotting_configuration.output}/{plotting_configuration.name}_{benchmark}.{plotting_configuration.format}",
            dpi=plotting_configuration.dpi
            )

    return None


def get_global_range(benchmark_data: util.BenchmarkData) -> tuple[float, float]: 

    minimum: float = float('inf')
    maximum: float = 0.0

    for order in benchmark_data:
        for method in order:

            # collect min and max for all tuning runs for this method
            method_performance_min: list[float] = []
            method_performance_max: list[float] = []
            for tuning_run in order[method]:
                # get min/max for this tuning run 
                method_performance_min.append(min([sample.runtime for sample in tuning_run]))
                # for performance evolution we need the first default configuration, which might be better than the worst
                method_performance_max.append(tuning_run[0].runtime)

            # compare if mean of min/max is the new global min/max
            if(np.mean(method_performance_min)) < minimum:
                minimum = float(np.mean(method_performance_min))
            
            if(np.mean(method_performance_max)) > maximum:
                maximum = float(np.mean(method_performance_max))

    return (minimum, maximum)

