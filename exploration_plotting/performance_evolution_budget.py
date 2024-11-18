#!/bin/python3.10
from __future__ import annotations

from typing import (
    List,
    Dict,
    Tuple,
    Callable,
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

from scipy.stats import sem # type: ignore

import util

@staticmethod
def performance_evolution_budget(plotting_configuration: PlottingConfiguration) -> None:

    multiple_exploration_data_runtime: util.MultipleExplorationDataRuntime = util.get_multiple_data(
        input=plotting_configuration.input
        )

    # create pe plot for each benchmark 
    for benchmark in sorted(multiple_exploration_data_runtime.keys()):

        try:
            performance_evolution_plot(plotting_configuration=plotting_configuration, 
                                       benchmark=benchmark,
                                       exploration_data=multiple_exploration_data_runtime[benchmark],
                                       plotting=performance_evolution_method_means,
                                      )
        except Exception as e:
            print(f"Error: {benchmark}")
            print(f"Error: {e}")

    return None

@staticmethod
def performance_evolution_plot(plotting_configuration: PlottingConfiguration, 
                               benchmark: str,
                               exploration_data: util.ExplorationDataRuntime,
                               plotting: Callable[[PlottingConfiguration, str, util.MethodDataRuntime, str, Any], Tuple[List[float], List[float]]],
                               ) -> None: 

    plt.clf()
    plt.figure( # type: ignore
        figsize=plotting_configuration.figsize, 
        dpi=plotting_configuration.dpi
        ) 

    fig, axles= plt.subplots(2, 2, figsize=(7, 6))  # 2 rows, 2 column # type: ignore
    fig.suptitle(f"{util.names_map[benchmark]}", fontweight="bold", fontsize=12) # type: ignore

    # create one plot for each method, pairwise  
    methods: list[str] = list(filter(lambda x: len(x.split('_')) <= 1, exploration_data.keys()))

    method_counter: int = 0
    for method in sorted(methods):

        try: 

            method_data: util.MethodDataRuntime = exploration_data[method][1]
            method_data_budget: util.MethodDataRuntime = exploration_data[method + f"_adjusted"][1]

            # method full
            full: Tuple[List[float], List[float]] = plotting(plotting_configuration, 
                "Tuning Budget: 50",
                method_data,
                '#1a5e92',
                axles.flat[method_counter], # type: ignore
                )

            # method budget 
            budget: Tuple[List[float], List[float]] = plotting(plotting_configuration, 
                f"Tuning Budget: {util.tuning_budget_map[benchmark]}",
                method_data_budget,
                '#ff7f0e', # orange
                axles.flat[method_counter], # type: ignore 
                )

            # plot line in between 
            # method 

            # x = last 
            # y = min 
            budget_min: Tuple[float, float] = (budget[0][-1], min(budget[1]))

            budget_min_point: Tuple[float, float] = (budget[1].index(min(budget[1])), min(budget[1]))

            # x = point of clash
            # y = min 
            # get clash 

            # Initialize indices for lower and upper bounds
            lower_index: int = 0

            # Iterate through the sorted list to find the surrounding values
            target: float = budget_min[1]
            print(f"Target: {target}") # type: ignore
            for i, value in enumerate(full[1]):
                if value > target:
                    lower_index = i
                elif value < target:
                    # upper_index = i
                    break


            # x_clash: int = full[0].index(budget_min[0]) # does not have this index 
            full_min: Tuple[float, float] = ((lower_index + 0.5), min(budget[1]))

            # warning, use index of minium, not of the end! 
            # print(f"start full: {full[1][0]}") # type: ignore
            # print(f"start budget: {budget[1][0]}") # type: ignore
            # print(f"min full: {min(full[1])}") # type: ignore
            # print(f"min budget: {budget_min[1]}") # type: ignore

            speedup_full: float = full[1][0]/min(full[1])
            speedup_budget: float = full[1][0]/budget_min[1]

            speedup_proportion: float = speedup_budget/speedup_full

            # how fast does budget get the performance of full 
            # print(f"speeudp_full: {speedup_full}")
            # print(f"speedup_budget: {speedup_budget}")
            # print(f"speedup_proportion: {speedup_proportion}")
            # print("\n")

            # compute position, where speedup is reached 
            budget_propotion: float = budget_min_point[0]/full_min[0] 

            # get portion of that 
            speedup_proportion_string: str = f"{speedup_proportion:.2%}"
            budget_propotion_string: str = f"{budget_propotion:.2%}"
            axles.flat[method_counter].plot([full_min[0], budget_min_point[0]], [full_min[1], budget_min_point[1]], lw=1, color='black', alpha=0.8, label=f"Speedup: {speedup_proportion_string} \nSamples: {budget_propotion_string}", zorder=2) # type: ignore

            # budget_min_point[1] < full_min[1]

            axles.flat[method_counter].scatter(full_min[0], # type: ignore 
                        full_min[1], 
                        alpha=1, 
                        color='black', 
                        marker='.',
                        lw=1, 
                        zorder=3
                        )

            axles.flat[method_counter].scatter(budget_min_point[0], # type: ignore 
                        budget_min_point[1], 
                        alpha=1, 
                        color='black', 
                        marker='.',
                        lw=1, 
                        zorder=3
                        )

            axles.flat[method_counter].set_title(f"{util.names_map[method]}", fontweight="bold") # type: ignore

            # x-axis 
            axles.flat[method_counter].set_xlim(left=util.left_right[benchmark][0], right=util.left_right[benchmark][1]) # type: ignore
            axles.flat[method_counter].set_xlabel("Samples") # type: ignore

            # y-axis 
            axles.flat[method_counter].set_yscale('log') # type: ignore 
            axles.flat[method_counter].set_ylim(bottom=util.bottom_top[benchmark][0], top=util.bottom_top[benchmark][1]) # type: ignore
            axles.flat[method_counter].set_ylabel("Runtime (ms)") # type: ignore
            axles.flat[method_counter].yaxis.set_major_formatter(FuncFormatter(util.log_formatter)) # type: ignore

            legend = axles.flat[method_counter].legend() # type: ignore
            legend.get_frame().set_visible(True) # type: ignore
            legend.get_frame().set_facecolor("white")  # Set the frame face color to white # type: ignore
            legend.get_frame().set_edgecolor("black")  # Set the border color # type: ignore
            legend.get_frame().set_linewidth(1.5)      # Set the border line width # type: ignore

            method_counter += 1

        except Exception as e:
            print(f"error: {e}")
            pass
                
      # plot expert 
    if plotting_configuration.expert:

        if plotting_configuration.log:
            expert: float = np.log10(
                plotting_configuration.expert if plotting_configuration.unit == 'runtime' else util.get_gflops(
                    plotting_configuration.expert))
        else:
            expert: float= plotting_configuration.expert if plotting_configuration.unit == 'runtime' else util.get_gflops(
                plotting_configuration.expert)

        plt.axhline(y=expert, color='black', linestyle='-', label='Expert', alpha=0.5) # type: ignore 

    # plot default 
    if plotting_configuration.default:

        if plotting_configuration.log:
            default: float = np.log10(
                plotting_configuration.default if plotting_configuration.unit == 'runtime' else util.get_gflops(
                    plotting_configuration.default))
        else:
            default: float = plotting_configuration.default if plotting_configuration.unit == 'runtime' else util.get_gflops(
                plotting_configuration.default)

        plt.axhline(y=default, color='black', linestyle='-', label='Default', alpha=0.5) # type: ignore 

    plt.tight_layout() # type: ignore

    # save to file
    log_appendix: str = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}_{benchmark}{log_appendix}.{plotting_configuration.format}",
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

@staticmethod
def performance_evolution_method_means(plotting_configuration: PlottingConfiguration, 
                                       method_key: str, 
                                       method_data: util.MethodDataRuntime, 
                                       color: str,
                                       axis: Any
                                       ) -> Tuple[List[float], List[float]]:

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
             alpha=1, 
             color=color, 
             lw=2, 
             label=method_key,
             zorder=1
             )

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

    return (list(x), means)
