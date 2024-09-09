#!/bin/python3.10
from __future__ import annotations

from typing import (
    List,
    Dict,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

from matplotlib import pyplot as plt
import numpy as np

from scipy.stats import sem # type: ignore

import util

plt.style.use('seaborn-v0_8-darkgrid')

@staticmethod
def tuning_ranges(plotting_configuration: PlottingConfiguration) -> None: 
    # get data an group after tuning 
    exploration_data: util.ExplorationData = util.get_data_fully(plotting_configuration.input)

    # set x and y range for all plots at least for one method 
    # set dynamic size of plots width, height, line-width

    for method in exploration_data:
        count: int = 0
        # reset figure 
        plt.clf()

        plt.figure( # type: ignore
            figsize=plotting_configuration.figsize, 
            dpi=plotting_configuration.dpi
        ) 


        for run in exploration_data[method][1]:
            count += 1

            print(f"run: {run}")

            exploration_data[method]

            grouped_by_tuning: List[List[Dict[str, str]]] = util.group_by_tuning(exploration_data[method][1][run])

            values_max: List[float] = []
            values_min: List[float] = []

            invalid_limit: int = 10**4

            for group in grouped_by_tuning:

                minimum: float = 0.0
                maximum: float = 0.0

                # get valid runtimes 
                runtimes_valid: List[float] = [float(line['runtime']) for line in group if float(line['runtime']) > 0]

                if len(runtimes_valid) > 0:

                    # get min and max of all values 
                    minimum = min(runtimes_valid)

                    # get first element of tuning run  
                    maximum = [float(line['runtime']) for line in group][0]
                    if maximum < 0:
                        maximum = invalid_limit
               
                else: 
                    # all values are invalid 
                    minimum = invalid_limit - 1000
                    maximum = invalid_limit

                if len(runtimes_valid) > 0 or plotting_configuration.plot_invalid: 

                    # if value are equal, increase size of bar slightly
                    # TODO add dynamic computation of margin based on overall range
                    if minimum == maximum:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum) + np.log10(1.1))
                            values_min.append(np.log10(minimum))
                        else:
                            values_max.append(maximum + 1.1)
                            values_min.append(minimum)
                    
                    else:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum))
                            values_min.append(np.log10(minimum))
                        else:
                            values_max.append(maximum)
                            values_min.append(minimum)

            # set x axis 
            x: List[int] = list(range(len(values_max)))

            # compute colors
            # colors_values: List[str] = ['#C44E52' if value_max == np.log10(invalid_limit) else '#4C72B0' for value_max in values_max]
            colors_values: List[str] = ['#4C72B0' for _ in values_max]

            # convert maximum to height 
            values_max = [max_val - min_val for max_val, min_val in zip(values_max, values_min)]

            # add bars 
            plt.subplot(1, len(exploration_data[method][1]), count) # type: ignore
            # plt.subplot(count) # type: ignore

            plt.xlim(left=0, right=len(values_min)) # type: ignore
            plt.ylim(bottom=-2.5, top=4) # type: ignore

            # assemble plot
            # plt.title(f"{plotting_configuration.name} - {method} - Tuning Ranges", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.title(f"{run}", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.xlabel("Rewrites") # type: ignore
            plt.ylabel("Performance Range Runtime (ms) log" if plotting_configuration.log else "Performance Range Runtime (ms)") # type: ignore 
            # plt.ylim(10**-6, 10)
            plt.bar(x=x, height=values_max, bottom=values_min, width=1, color=colors_values) # type: ignore

            # add line for performance evolution

            # init minimum with first valid value found 
            # warning: invalid values have the value: invalid_limit
            pe: List[float] = []
            minimum: float = 0
            for value in values_min:
                minimum = value
                break
                    
            # create performance evolution 
            # warning: invalid values have the value: invalid_limit
            for value in values_min:
                if value < minimum:
                    minimum = value
                pe.append(minimum)

            pe_x: List[int] = list(range(len(pe)))

            # plot performance evolution
            plt.plot(pe_x, # type: ignore
                     pe, 
                     alpha=0.9, 
                    #  color='#4EC4B0', # teal green 
                    #  color='#B0A64C', # mustard yellow 
                    # color='grey',
                    color='#C44E52', # red 
                    # color='#FFD700',
                     lw=2, 
                     label=run
                     ) 

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



        # save to file
        log_appendix: str = ""
        if plotting_configuration.log:
            log_appendix = "_log"

        invalid_appendix: str = ""
        if plotting_configuration.plot_invalid:
            invalid_appendix = "_invalid"

        plt.tight_layout(pad=2.0)
        plt.savefig( # type: ignore
            f"{plotting_configuration.output}/{plotting_configuration.name}_{method}_tuning_ranges{log_appendix}{invalid_appendix}.{plotting_configuration.format}",
            dpi=plotting_configuration.dpi)

