#!/bin/python3.10
from __future__ import annotations

from typing import (
    List,
    Dict,
    Callable,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

from scipy.stats import sem # type: ignore

import util

@staticmethod
def performance_evolution(plotting_configuration: PlottingConfiguration) -> None:

    exploration_data: util.ExplorationDataRuntime = util.get_data(
        input=plotting_configuration.input
        )

    performance_evolution_plot(plotting_configuration=plotting_configuration, 
                               exploration_data=exploration_data,
                               plotting=performance_evolution_method_means,
                               )

    return None


@staticmethod
def performance_evolution_plot(plotting_configuration: PlottingConfiguration, 
                               exploration_data: util.ExplorationDataRuntime,
                               plotting: Callable[[PlottingConfiguration, str, util.MethodDataRuntime, str], None],
                               ) -> None: 

    plt.figure( # type: ignore
        figsize=plotting_configuration.figsize, 
        dpi=plotting_configuration.dpi
        ) 

    fig, ax = plt.subplots(figsize=(5, 5)) # type: ignore

    method_keys: list[str] = sorted(exploration_data.keys())

    counter: int = 0
    for method_key in method_keys:

        plotting(plotting_configuration, 
                 method_key,
                 exploration_data[method_key][1], 
                 util.colors[counter % len(util.colors)]
                 )

        counter += 1

    # assemble plot
    plt.title(f"{plotting_configuration.name} - Performance Evolution", fontsize=plotting_configuration.fontsize) # type: ignore 
    plt.xlabel("Samples") # type: ignore
    plt.ylabel("Runtime (ms)") # type: ignore 

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


    # y-axis log scale 
    ax.set_yscale('log') # type: ignore 
    ax.yaxis.set_major_formatter(FuncFormatter(util.log_formatter)) # type: ignore

    plt.tight_layout() # type: ignore
    plt.legend() # type: ignore 

    # save to file
    log_appendix: str = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}_{(str(plotting).split('_')[-1]).split(' ')[0]}{log_appendix}.{plotting_configuration.format}",
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
                                       color: str
                                       ):

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
    plt.plot(x,  # type: ignore 
             means, 
             alpha=0.8, 
             color=color, 
             lw=3, 
             label=method_key
             )

    # plot confidence interval
    lower: List[float] = []
    upper: List[float] = []
    for i in range(len(means)):
        lower.append(means[i] - confidence[i])
        upper.append(means[i] + confidence[i])

    # plt.fill_between(x,  # type: ignore 
    #                  lower, 
    #                  upper, 
    #                  color=color, 
    #                  alpha=0.2
    #                  ) 

    return None
