#!/bin/python3.10
from __future__ import annotations

from typing import (
    List,
    Dict,
    Tuple,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
import numpy as np

from scipy.stats import sem # type: ignore

import util

@staticmethod
def performance_evolution_grouped(plotting_configuration: PlottingConfiguration) -> None:

    performance_evolution_plot(plotting_configuration=plotting_configuration)

    return None


@staticmethod
def performance_evolution_plot(plotting_configuration: PlottingConfiguration) -> None: 

    # get data 
    multiple_exploration_data_runtime: util.MultipleExplorationData = util.get_multiple_data_fully(plotting_configuration.input)

    # create figure with a grid 
    plt.clf()
    plt.figure( # type: ignore
        figsize=(20, 12),  # is this ignored?
        dpi=plotting_configuration.dpi
    )
    fig, axes = plt.subplots(2, 3, figsize=(12, 5))  # 2 rows, 3 column # type: ignore

    benchmark_count = 0
    for benchmark in sorted(benchmarks_to_plot):

        multiple_exploration_data_runtime[benchmark]

        performance_evolution_benchmark(plotting_configuration=plotting_configuration, 
                                        benchmark=benchmark, 
                                        benchmark_data=multiple_exploration_data_runtime[benchmark], 
                                        axis=axes.flat[benchmark_count],  # type: ignore
                                        ) # type: ignore 
        benchmark_count += 1

    # Collect all handles and labels from the first subplot (or any of them since they're the same)
    handles, labels = axes[0, 0].get_legend_handles_labels() # type: ignore

    # '#1f77b4', # blue 
    # '#ff7f0e', # orange 
    # '#2ca02c', # green 
    # '#d62728', # red 
    # '#e377c2', # coral

    # moved by one 
    custom_lines = [
        Line2D([0], [0], color="#1f77b4", lw=2, linestyle="-"), # BFS
        Line2D([0], [0], color="#ff7f0e", lw=2, linestyle="-"), # LS
        Line2D([0], [0], color="#2ca02c", lw=2, linestyle="-"), # MCTS
        Line2D([0], [0], color="#d62728", lw=2, linestyle="-"), # RS
        Line2D([0], [0], color="black", lw=2, linestyle="-"), # Expert
    ]

    # add colors here 
    custom_labels = [
        "Breadth-First Search",
        "Local Search",
        "MCTS",
        "Random Sampling",
        "Expert"
    ]

    # Place the legend in the empty space of the 6th "invisible" subplot
    legend = fig.legend(custom_lines, custom_labels, loc="center", bbox_to_anchor=(0.83, 0.25), ncol=1) # type: ignore


    legend.get_frame().set_visible(True) # type: ignore
    legend.get_frame().set_facecolor("white")  # Set the frame face color to white # type: ignore
    legend.get_frame().set_edgecolor("black")  # Set the border color # type: ignore
    legend.get_frame().set_linewidth(1.5)      # Set the border line width # type: ignore
    axes.flat[5].axis("off")  # Turn off the sixth subplot # type: ignore 

    plt.tight_layout() # type: ignore

    # save to file
    log_appendix: str = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}_{(str().split('_')[-1]).split(' ')[0]}{log_appendix}.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)

    return None


@staticmethod
def performance_evolution_method_separate(plotting_configuration: PlottingConfiguration,
                                          method_key: str,
                                          method_data: util.MethodDataRuntime,
                                          color: str
                                          )-> None:

    # get runtimes from individual runs of method 
    data_internal: Dict[str, List[float]] = {}
    for key in method_data:
        internal: List[float]  = []
        for elem in method_data[key]:
            internal.append(elem[1])

        data_internal[key] = internal

    # convert data to represent performance evolution
    for key in data_internal:
        pe: List[float] = []
        minimum: float = data_internal[key][0]
        for elem in data_internal[key]:
            if elem < minimum:
                minimum = elem

            if plotting_configuration.log:
                if plotting_configuration.unit == "gflops":
                    pe.append(np.log10(util.get_gflops(minimum)))
                else:
                    pe.append(np.log10(minimum))
            else:
                if plotting_configuration.unit == "gflops":
                    pe.append(util.get_gflops(minimum))
                else:
                    pe.append(minimum)

        data_internal[key] = pe

    # create one pe graph for each run in method 
    counter: int = 0

    for run in data_internal:

        # create x-axis and y-axis for plot 
        x: List[int] = list(range(len(data_internal[run])))
        y: List[float] = data_internal[run]

        # cut x and y if necessary
        if plotting_configuration.limit:
            x = x[:plotting_configuration.limit]
            y = y[:plotting_configuration.limit]

        # create plot 
        plt.plot(x, # type: ignore
                 y, 
                 alpha=0.9, 
                #  color=colors[counter % len(colors)], 
                 color=color, 
                 lw=1,
                 label=f"{method_key}_{run[:-4]}"
                 )

        counter += 1

    return None

bottom_top: Dict[str, Tuple[float, float]] = {
    "acoustic" : (0.01, 100),
    "asum" : (0.005, 1000),
    "kmeans" : (0.01, 1000),
    "mm" : (2, 25000),
    "mm_2070" : (1, 30000),
    "scal" : (0.25, 3000),
}

left_right: Dict[str, Tuple[float, float]] = {
    "acoustic" : (0,  6000), # or max 
    "asum" : (0, 5000),
    "kmeans" : (0, 4000),
    "mm" : (0, 10000),
    "mm_2070" : (0, 36000),
    "scal" : (0, 3500),
}                                   

color_map: Dict[str, str] = {
    "MCTS": '#1f77b4',
    "Exhaustive": '#1f77b4',
    "RandomGraph": '#1f77b4',
    "LocalSearch": '#ff7f0e',
}

expert: Dict[str, float] = {
    "acoustic" : 0.018432, # final
    "asum" : 0.01536, # final
    "kmeans" : 0.017408, # final 
    "mm_bak" : 1.065984, # final
    "mm" : 2.55664, # final
    "mm_2070" : 2.55664, # final
    "scal" : 0.34816, # final
}                                   

methods_to_plot: List[str] = [
    "MCTS_adjusted",
    "RandomGraph_adjusted",
    "LocalSearch_adjusted",
    "Exhaustive_adjusted",
]

benchmarks_to_plot: List[str] = [
    "acoustic",
    "asum",
    "kmeans",
    "mm",
    "scal",
]

@staticmethod
def performance_evolution_benchmark(plotting_configuration: PlottingConfiguration, 
                                    benchmark: str, 
                                    benchmark_data: util.ExplorationData, 
                                    axis: plt.Axes, # type: ignore
                                    ) -> None: 

    axis.set_title(util.names_map[benchmark], fontweight="bold") # type: ignore
    axis.set_yscale('log') # type: ignore 
    axis.yaxis.set_major_formatter(FuncFormatter(util.log_formatter)) # type: ignore

    # assemble plot
    axis.set_xlabel("Samples") # type: ignore
    axis.set_ylabel("Runtime (ms)") # type: ignore

    axis.set_xlim(left=left_right[benchmark][0], right=left_right[benchmark][1]) # type: ignore
    axis.set_ylim(bottom=bottom_top[benchmark][0], top=bottom_top[benchmark][1]) # type: ignore

    # create pe graph for each method
    method_count = 0
    # for method in sorted(benchmark_data.keys()):
    for method in sorted(methods_to_plot):
        # create plot for each method 
        try:
            performance_evolution_method_means(plotting_configuration=plotting_configuration, 
                                           benchmark=benchmark,
                                           method_key=util.names_map[method], 
                                           method_data=benchmark_data[method][1],  # why one here
                                           axis=axis, # type: ignore
                                           color=util.colors[method_count % len(util.colors)]
                                           )
        except KeyError:
            pass

        method_count += 1

    return None


@staticmethod
def performance_evolution_method_means(plotting_configuration: PlottingConfiguration, 
                                       benchmark: str,
                                       method_key: str, 
                                       method_data: util.MethodData, 
                                       axis: axes, # type: ignore
                                       color: str
                                       ) -> None:

    # convert to method data runtime
    method_data_runtime: util.MethodDataRuntime = {}
    for run in method_data:
        run_data: util.RunDataRuntime = []
        for sample in method_data[run]:
            if (str(sample['runtime']) == '-1'):
                run_data.append((False, float(2147483647)))
            else:
                run_data.append((True, float(sample['runtime'])))
        method_data_runtime[run] = run_data

    # get runtimes from individual runs of method 
    data_internal: Dict[str, List[float]] = {}
    for method in method_data_runtime:
        internal: List[float]  = []
        for sample in method_data_runtime[method]:
            internal.append(sample[1])

        data_internal[method] = internal

    # convert data to represent performance evolution
    for key in data_internal:
        pe: List[float] = []
        minimum: float = data_internal[key][0]
        for elem in data_internal[key]:
            if elem < minimum:
                minimum = elem

            if plotting_configuration.log:
                if plotting_configuration.unit == "gflops":
                    pe.append(np.log10(util.get_gflops(minimum)))
                else:
                    pe.append(np.log10(minimum))
            else:
                if plotting_configuration.unit == "gflops":
                    pe.append(util.get_gflops(minimum))
                else:
                    pe.append(minimum)

        data_internal[key] = pe

    # prepare: put data of individual runs to a list of list instead of a dictionary
    counter: int = -1
    means: List[float] = []
    runs_of_method: List[List[float]] = []
    confidence: List[float] = []
    
    for key in data_internal:
        counter += 1
        runs_of_method.append([])
        for elem in data_internal[key]:
            runs_of_method[counter].append(elem)

    # get shortest run and cut here 
    minElem: int = min(list(map(lambda x: len(x), runs_of_method)))

    # compute mean 
    for i in range(minElem):

        # group all runs at position i 
        runs_at_position: List[float] = [run[i] for run in runs_of_method]

        # compute mean for all runs at position i
        means.append(float(np.median(np.array(runs_at_position))))

        # compute confidence interval  
        confidence.append(sem(runs_at_position) * 1.96) 

    # create x range for plotting 
    # cut means and x if necessary 
    x = range(len(means))
    if plotting_configuration.limit:
        x = x[:plotting_configuration.limit]
        means = means[:plotting_configuration.limit]

    # plot means 
    axis.plot(x,  # type: ignore 
             means, 
             alpha=0.9, 
             color=color, 
             lw=2, 
             label=method_key
             )

    axis.scatter(x[-1],  # type: ignore 
             means[-1], 
             alpha=0.9, 
             color=color, 
             marker='x',
             lw=2, 
             )

    axis.axhline(y=expert[benchmark], color='black', linestyle='-', label='Expert', alpha=1) # type: ignore 

    # plot confidence interval
    lower: List[float] = []
    upper: List[float] = []
    for i in range(len(means)):
        lower.append(means[i] - confidence[i])
        upper.append(means[i] + confidence[i])

    # axis.fill_between(x,  # type: ignore 
    #                  lower, 
    #                  upper, 
    #                  color=color, 
    #                  alpha=0.2
    #                  ) 

    return None
