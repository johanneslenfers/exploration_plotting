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
import numpy as np

from scipy.stats import sem # type: ignore

import util
from matplotlib.ticker import LogFormatter
from matplotlib.ticker import FuncFormatter

plt.style.use('seaborn-v0_8-darkgrid')

@staticmethod
def tuning_ranges_playground(plotting_configuration: PlottingConfiguration) -> None: 
    tuning_ranges_dots(plotting_configuration)
    # tuning_ranges_old(plotting_configuration)
    # tuning_ranges_pe(plotting_configuration)
    # tuning_ranges_bars(plotting_configuration)

limits: List[int] = [1, 10, 20, 30, 40, 50]

def tuning_ranges_dots(plotting_configuration: PlottingConfiguration) -> None:

    multiple_exploration_data: util.MultipleExplorationData = util.get_multiple_data_fully(plotting_configuration.input)

    benchmark_counter = 0
    # for benchmark in multiple_exploration_data:
    for benchmark in sorted(multiple_exploration_data.keys()):

        tuning_ranges_dots_benchmark(plotting_configuration = plotting_configuration, 
                                     benchmark = benchmark,
                                     benchmark_data = multiple_exploration_data[benchmark],
                                     )
        benchmark_counter += 1


    return None


bottom_top: Dict[str, Tuple[float, float]] = {
    "acoustic" : (0.1, 10000),
    "asum" : (0.001, 100000),
    "kmeans" : (0.01, 100000),
    "mm" : (1, 10000),
    "mm_2070" : (1, 10000),
    "scal" : (0.1, 10000),
}

left_right: Dict[str, Tuple[float, float]] = {
    "acoustic" : (0,  1000), # or max 
    "asum" : (0, 150),
    "kmeans" : (0, 1000),
    "mm" : (0, 1000),
    "mm_2070" : (0, 850),
    "scal" : (0, 1000),
}                                   

# with data and benchmark key 
def tuning_ranges_dots_benchmark(plotting_configuration: PlottingConfiguration, 
                                 benchmark: str, 
                                 benchmark_data: util.ExplorationData,
                                 ) -> None:

    # implement tuning ranges with dots here

    exhaustive: util.MethodData = benchmark_data['Exhaustive'][1]

    # create plot with axis and grid 
    plt.clf()
    plt.figure( # type: ignore
        figsize=(20, 12),  # is this ignored?
        dpi=plotting_configuration.dpi
    )
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))  # 2 rows, 2 column # type: ignore

    limit_counter: int = 0

    print(f"benchmark: {benchmark}")

    for limit in limits: 
        for run in exhaustive:
            # print(f"run: {run} for lmit: {limit}")
            tuning_runs: List[util.TuningRunData] = util.group_by_tuning(exhaustive[run])

            # dots: Tuple[List[float], List[float]] = plot_dots_limit(tuning_runs=tuning_runs, limit=limit)
            dots: Dict[str, Tuple[List[float], List[float]]] = plot_dots_limit_colored(tuning_runs=tuning_runs, limit=limit, color_limit=10)

            # split into differently colored dots 

            # dots_colored: List[float] = sorted(dots[1])[:10]

            # plot means 
            axes.flat[limit_counter].scatter( # type: ignore
                dots["normal"][0], 
                dots['normal'][1], 
                color='#1a5e92', 
                alpha=0.9, 
                s=1,  # size of the dots
                label=f"{limit}"
            )

            axes.flat[limit_counter].scatter( # type: ignore
                dots['colored'][0], 
                dots['colored'][1], 
                color='red', 
                alpha=0.9, 
                s=2,  # size of the dots
                label=f"{limit}"
            )

            axes.flat[limit_counter].set_xlim(left=left_right[benchmark][0], right=left_right[benchmark][1]) # type: ignore
            axes.flat[limit_counter].set_ylim(bottom=bottom_top[benchmark][0], top=bottom_top[benchmark][1]) # type: ignore

            axes.flat[limit_counter].set_yscale('log') # type: ignore 
            axes.flat[limit_counter].yaxis.set_major_formatter(FuncFormatter(util.log_formatter)) # type: ignore

            axes.flat[limit_counter].legend() # type: ignore

        limit_counter += 1

    print("\n")

    # create plot 
    plt.tight_layout() # type: ignore

    # save to file
    log_appendix: str = ""
    if plotting_configuration.log:
        log_appendix = "_log"

    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}_dots_{benchmark}{log_appendix}.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)

    pass

def plot_dots_limit_colored(tuning_runs: List[util.TuningRunData], limit: int, color_limit: int) -> Dict[str, Tuple[List[float], List[float]]]:

    # normal
    x: List[float] = []
    y: List[float] = []

    # colored
    x_colored: List[float] = []
    y_colored: List[float] = []

    # cut runs here 
    tuning_runs_cut: List[util.TuningRunData] = [run[:limit] for run in tuning_runs]
    
    # create a dot for each value per tuning run 
    run_counter: int = 0
    for run in tuning_runs_cut:
        runtimes: List[float] = [float(line['runtime']) for line in run]


        for runtime in runtimes:
            x.append(run_counter)
            if runtime < 0:
                y.append(10000) # invalid value 
            else:
                y.append(runtime)
        
        runtimes_colored= sorted(runtimes)[:color_limit]

        for runtime in runtimes_colored:
            x_colored.append(run_counter)
            if runtime < 0:
                y_colored.append(10000) # invalid value 
            else:
                y_colored.append(runtime)

        run_counter += 1

    # x axis: tuning run 
    # y axis: runtime whitin the tuning run 

    return {
        "normal": (x,y),
        "colored": (x_colored, y_colored)
    }


def plot_dots_limit(tuning_runs: List[util.TuningRunData], limit: int) -> Tuple[List[float], List[float]]:

    x: List[float] = []
    y: List[float] = []

    # cut runs here 
    tuning_runs_cut: List[util.TuningRunData] = [run[:limit] for run in tuning_runs]
    
    # create a dot for each value per tuning run 
    run_counter: int = 0
    for run in tuning_runs_cut:
        runtimes: List[float] = [float(line['runtime']) for line in run]


        for runtime in runtimes:
            x.append(run_counter)
            if runtime < 0:
                y.append(10000) # invalid value 
            else:
                y.append(runtime)
        
        run_counter += 1
    
    # x axis: tuning run 
    # y axis: runtime whitin the tuning run 

    return (x, y)


def tuning_ranges_bars(plotting_configuration: PlottingConfiguration) -> None:  
    # get data an group after tuning 
    exploration_data: util.ExplorationData = util.get_data_fully(plotting_configuration.input)

    # set x and y range for all plots at least for one method 
    # set dynamic size of plots width, height, line-width

    # tuning budget 
    # tuning_budget: int = 50

    for method in exploration_data:
        count: int = 0
        # reset figure 
        plt.clf()

        plt.figure( # type: ignore
            figsize=plotting_configuration.figsize, 
            dpi=plotting_configuration.dpi
        ) 

        # fig, ax = plt.subplots(figsize=(16, 8)) # type: ignore

        for run in exploration_data[method][1]:
            count += 1

            print(f"run: {run}")

            exploration_data[method]

            grouped_by_tuning: List[List[Dict[str, str]]] = util.group_by_tuning(exploration_data[method][1][run])
            
            # cut samples 
            # grouped_by_tuning = [group[:tuning_budget] for group in grouped_by_tuning]
            values_max: List[float] = []
            values_min: List[float] = []

            # get min for all limited values 
            pe_for_limit: Dict[str, List[float]] = {}
            limits: List[int] = [1, 5, 10, 25]
            # limits: List[int] = [10, 20, 30, 40, 50]
            for limit in limits:
                pe_for_limit[str(limit)] = [] 

            invalid_limit: int = 10**4

            points_for_run: List[List[float]] = []

            for group in grouped_by_tuning:

                minimum: float = 0.0
                maximum: float = 0.0
                
                # get all points 
                points: list[float] = []
                points = [float(line['runtime']) for line in group]
                points = [invalid_limit if point == -1.0 else point for point in points]
                points_for_run.append(points)

                # get valid runtimes 
                runtimes_valid: List[float] = [float(line['runtime']) for line in group if float(line['runtime']) > 0]

                # get valid runtimes until certain limit 
                runtimes_valid_limit: Dict[str, List[float]] = {} 
                minima_for_limits: Dict[str, float] = {}

                # limits: List[int] = [] 
                for limit in limits:
                    runtimes_valid_limit[str(limit)] = [float(line['runtime']) for line in group[:limit] if float(line['runtime']) > 0]

                if len(runtimes_valid) > 0:

                    # get min and max of all values 
                    minimum = min(runtimes_valid)

                    # get first element of tuning run  
                    maximum = [float(line['runtime']) for line in group][0]
                    if maximum < 0:
                        maximum = invalid_limit
               
                    # get minima for all limits 
                    for limit in limits:
                        if len(runtimes_valid_limit[str(limit)]) == 0:
                            minima_for_limits[str(limit)] = invalid_limit - 1000
                        else:
                            minima_for_limits[str(limit)] = min(runtimes_valid_limit[str(limit)])
              
                else: 
                    # all values are invalid 
                    minimum = invalid_limit - 1000
                    maximum = invalid_limit

                    for limit in limits:
                        minima_for_limits[str(limit)] = invalid_limit - 1000

                if len(runtimes_valid) > 0 or plotting_configuration.plot_invalid: 

                    # if value are equal, increase size of bar slightly
                    # TODO add dynamic computation of margin based on overall range
                    if minimum == maximum:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum) + np.log10(1.1))
                            values_min.append(np.log10(minimum))

                            for limit in limits:
                                pe_for_limit[str(limit)].append(np.log10(minima_for_limits[str(limit)]))

                        else:
                            values_max.append(maximum + 1.1)
                            values_min.append(minimum)

                            for limit in limits:
                                pe_for_limit[str(limit)].append(minima_for_limits[str(limit)])
                    else:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum))
                            values_min.append(np.log10(minimum))

                            for limit in limits:
                                pe_for_limit[str(limit)].append(np.log10(minima_for_limits[str(limit)]))

                        else:
                            values_max.append(maximum)
                            values_min.append(minimum)
                            for limit in limits:
                                pe_for_limit[str(limit)].append(minima_for_limits[str(limit)])
                

            # set x axis 
            x: List[int] = list(range(len(values_max)))

            # compute colors
            # colors_values: List[str] = ['#C44E52' if value_max == np.log10(invalid_limit) else '#4C72B0' for value_max in values_max]
            colors_values: List[str] = ['#4C72B0' for _ in values_max]

            # convert maximum to height 
            values_max = [max_val - min_val for max_val, min_val in zip(values_max, values_min)]

            # add bars 
            ax = plt.subplot(1, len(exploration_data[method][1]), count) # type: ignore
            # plt.subplot(count) # type: ignore

            plt.xlim(left=0, right=len(values_min)) # type: ignore

            # assemble plot
            # plt.title(f"{plotting_configuration.name} - {method} - Tuning Ranges", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.title(f"{plotting_configuration.name}", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.xlabel("Rewrites/Tuning Runs") # type: ignore
            plt.ylabel("Runtime (ms) log" if plotting_configuration.log else "Runtime (ms)") # type: ignore 
            # plt.ylim(10**-6, 10)
            plt.bar(x=x, height=values_max, bottom=values_min, width=0.5, alpha=0.8, color=colors_values, label=f"Performance Range") # type: ignore

            # add line for performance evolution
            ax.set_yscale('log') # type: ignore 

            # Use LogFormatter to show the actual values
            ax.yaxis.set_major_formatter(LogFormatter()) # type: ignore

            # add a scatter plot for all points

            x: List[int] = list(range(len(points_for_run)))

            for run in x:
                
                x_coordinates: list[int] = [run for _ in range(len(points_for_run[run]))]
                plt.scatter(x_coordinates, points_for_run[run], color='red', s=3) # type: ignore
                
                    
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

            legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),fancybox=True, shadow=True, ncol=3) # type: ignore

            # Change the background color of the legend
            legend.get_frame().set_facecolor('lightgray')

            # Optionally, you can also set the edge color and linewidth
            legend.get_frame().set_edgecolor('black')
            legend.get_frame().set_linewidth(2)
            plt.tight_layout
            # plt.legend(loc='lower right') # type: ignore


        # save to file
        log_appendix: str = ""
        if plotting_configuration.log:
            log_appendix = "_log"

        invalid_appendix: str = ""
        if plotting_configuration.plot_invalid:
            invalid_appendix = "_invalid"

        plt.tight_layout(pad=2.0)
        plt.savefig( # type: ignore
            f"{plotting_configuration.output}/{plotting_configuration.name}_{method}_tuning_ranges_bars_{log_appendix}{invalid_appendix}.{plotting_configuration.format}",
            dpi=plotting_configuration.dpi)



def tuning_ranges_pe(plotting_configuration: PlottingConfiguration) -> None:  
    # get data an group after tuning 
    exploration_data: util.ExplorationData = util.get_data_fully(plotting_configuration.input)

    # set x and y range for all plots at least for one method 
    # set dynamic size of plots width, height, line-width

    # tuning budget 
    # tuning_budget: int = 50

    for method in exploration_data:
        count: int = 0
        # reset figure 
        plt.clf()

        plt.figure( # type: ignore
            figsize=(8,8), 
            dpi=plotting_configuration.dpi
        ) 


        for run in exploration_data[method][1]:
            count += 1

            print(f"run: {run}")

            exploration_data[method]

            grouped_by_tuning: List[List[Dict[str, str]]] = util.group_by_tuning(exploration_data[method][1][run])
            
            # cut samples 
            # grouped_by_tuning = [group[:tuning_budget] for group in grouped_by_tuning]
            values_max: List[float] = []
            values_min: List[float] = []

            # get min for all limited values 
            pe_for_limit: Dict[str, List[float]] = {}
            limits: List[int] = [1, 5, 10, 25]
            # limits: List[int] = [10, 20, 30, 40, 50]
            for limit in limits:
                pe_for_limit[str(limit)] = [] 

            invalid_limit: int = 10**4

            for group in grouped_by_tuning:

                minimum: float = 0.0
                maximum: float = 0.0

                # get valid runtimes 
                runtimes_valid: List[float] = [float(line['runtime']) for line in group if float(line['runtime']) > 0]

                # get valid runtimes until certain limit 
                runtimes_valid_limit: Dict[str, List[float]] = {} 
                minima_for_limits: Dict[str, float] = {}

                # limits: List[int] = [] 
                for limit in limits:
                    runtimes_valid_limit[str(limit)] = [float(line['runtime']) for line in group[:limit] if float(line['runtime']) > 0]

                if len(runtimes_valid) > 0:

                    # get min and max of all values 
                    minimum = min(runtimes_valid)

                    # get first element of tuning run  
                    maximum = [float(line['runtime']) for line in group][0]
                    if maximum < 0:
                        maximum = invalid_limit
               
                    # get minima for all limits 
                    for limit in limits:
                        if len(runtimes_valid_limit[str(limit)]) == 0:
                            minima_for_limits[str(limit)] = invalid_limit - 1000
                        else:
                            minima_for_limits[str(limit)] = min(runtimes_valid_limit[str(limit)])
              
                else: 
                    # all values are invalid 
                    minimum = invalid_limit - 1000
                    maximum = invalid_limit

                    for limit in limits:
                        minima_for_limits[str(limit)] = invalid_limit - 1000

                if len(runtimes_valid) > 0 or plotting_configuration.plot_invalid: 

                    # if value are equal, increase size of bar slightly
                    # TODO add dynamic computation of margin based on overall range
                    if minimum == maximum:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum) + np.log10(1.1))
                            values_min.append(np.log10(minimum))

                            for limit in limits:
                                pe_for_limit[str(limit)].append(np.log10(minima_for_limits[str(limit)]))

                        else:
                            values_max.append(maximum + 1.1)
                            values_min.append(minimum)

                            for limit in limits:
                                pe_for_limit[str(limit)].append(minima_for_limits[str(limit)])
                    else:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum))
                            values_min.append(np.log10(minimum))

                            for limit in limits:
                                pe_for_limit[str(limit)].append(np.log10(minima_for_limits[str(limit)]))

                        else:
                            values_max.append(maximum)
                            values_min.append(minimum)
                            for limit in limits:
                                pe_for_limit[str(limit)].append(minima_for_limits[str(limit)])
                

            # set x axis 
            x: List[int] = list(range(len(values_max))) # type: ignore

            # compute colors
            # colors_values: List[str] = ['#C44E52' if value_max == np.log10(invalid_limit) else '#4C72B0' for value_max in values_max]
            colors_values: List[str] = ['#4C72B0' for _ in values_max] # type: ignore

            # convert maximum to height 
            values_max = [max_val - min_val for max_val, min_val in zip(values_max, values_min)]

            # add bars 
            ax = plt.subplot(1, len(exploration_data[method][1]), count) # type: ignore
        
            plt.xlim(left=0, right=len(values_min)) # type: ignore

            # assemble plot
            # plt.title(f"{plotting_configuration.name} - {method} - Tuning Ranges", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.title(f"{plotting_configuration.name}", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.xlabel("Rewrites/Tuning Runs") # type: ignore
            plt.ylabel("Runtime (ms) log" if plotting_configuration.log else "Runtime (ms)") # type: ignore 
            # plt.ylim(10**-6, 10)
            # plt.bar(x=x, height=values_max, bottom=values_min, width=1, color=colors_values, label=f"Performance Range") # type: ignore

            # add line for performance evolution
            ax.set_yscale('log') # type: ignore 

            # Use LogFormatter to show the actual values
            ax.yaxis.set_major_formatter(LogFormatter()) # type: ignore

            
            for limit in limits:
                # print(f"limit: {limit}")
                pe: List[float] = []
                minimum: float = 0
                # print(f"len: {len(pe_for_limit[str(limit)])}")
                for value in pe_for_limit[str(limit)]:
                    minimum = value
                    break

                # create performance evolution 
                # warning: invalid values have the value: invalid_limit
                for value in pe_for_limit[str(limit)]:
                    # print(f"value: {value}")
                    if value < minimum:
                        minimum = value
                    pe.append(minimum)
                
                pe_x: List[int] = list(range(len(pe)))

                # plot performance evolution
                plt.plot(pe_x, # type: ignore
                        pe, 
                        alpha=0.5, 
                        #  color='#4EC4B0', # teal green 
                        #  color='#B0A64C', # mustard yellow 
                        # color='grey',
                        # color='#C44E52', # red 
                        # color='#FFD700',
                        lw=2, 
                        label=f"Tuning Budget: {str(limit)}"
                        ) 


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
                     label="Tuning Budget: 50"
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

            legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),fancybox=True, shadow=True, ncol=3) # type ignore
            # legend = plt.legend()

            # Change the background color of the legend
            legend.get_frame().set_facecolor('lightgray')

            # Optionally, you can also set the edge color and linewidth
            legend.get_frame().set_edgecolor('black')
            legend.get_frame().set_linewidth(2)
            plt.tight_layout
            # plt.legend(loc='lower right') # type: ignore


        # save to file
        log_appendix: str = ""
        if plotting_configuration.log:
            log_appendix = "_log"

        invalid_appendix: str = ""
        if plotting_configuration.plot_invalid:
            invalid_appendix = "_invalid"

        plt.tight_layout(pad=2.0)
        plt.savefig( # type: ignore
            f"{plotting_configuration.output}/{plotting_configuration.name}_{method}_tuning_ranges_pe{log_appendix}{invalid_appendix}.{plotting_configuration.format}",
            dpi=plotting_configuration.dpi)


def tuning_ranges_old(plotting_configuration: PlottingConfiguration) -> None:  
    # get data an group after tuning 
    exploration_data: util.ExplorationData = util.get_data_fully(plotting_configuration.input)

    # set x and y range for all plots at least for one method 
    # set dynamic size of plots width, height, line-width

    # tuning budget 
    # tuning_budget: int = 50

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
            
            # cut samples 
            # grouped_by_tuning = [group[:tuning_budget] for group in grouped_by_tuning]
            values_max: List[float] = []
            values_min: List[float] = []

            # get min for all limited values 
            pe_for_limit: Dict[str, List[float]] = {}
            limits: List[int] = [1, 5, 10, 25]
            # limits: List[int] = [10, 20, 30, 40, 50]
            for limit in limits:
                pe_for_limit[str(limit)] = [] 

            invalid_limit: int = 10**4

            points_for_run: List[List[float]] = []

            for group in grouped_by_tuning:

                minimum: float = 0.0
                maximum: float = 0.0

                # get all points 
                points: list[float] = []
                points = [float(line['runtime']) for line in group]
                points = [invalid_limit if point == -1.0 else point for point in points]

                if plotting_configuration.log:
                    points_for_run.append([np.log10(point) for point in points])
                else: 
                    points_for_run.append(points)

                # get valid runtimes 
                runtimes_valid: List[float] = [float(line['runtime']) for line in group if float(line['runtime']) > 0]

                # get valid runtimes until certain limit 
                runtimes_valid_limit: Dict[str, List[float]] = {} 
                minima_for_limits: Dict[str, float] = {}

                # limits: List[int] = [] 
                for limit in limits:
                    runtimes_valid_limit[str(limit)] = [float(line['runtime']) for line in group[:limit] if float(line['runtime']) > 0]

                if len(runtimes_valid) > 0:

                    # get min and max of all values 
                    minimum = min(runtimes_valid)

                    # get first element of tuning run  
                    maximum = [float(line['runtime']) for line in group][0]
                    if maximum < 0:
                        maximum = invalid_limit
               
                    # get minima for all limits 
                    for limit in limits:
                        if len(runtimes_valid_limit[str(limit)]) == 0:
                            minima_for_limits[str(limit)] = invalid_limit - 1000
                        else:
                            minima_for_limits[str(limit)] = min(runtimes_valid_limit[str(limit)])
              
                else: 
                    # all values are invalid 
                    minimum = invalid_limit - 1000
                    maximum = invalid_limit

                    for limit in limits:
                        minima_for_limits[str(limit)] = invalid_limit - 1000

                if len(runtimes_valid) > 0 or plotting_configuration.plot_invalid: 

                    # if value are equal, increase size of bar slightly
                    # TODO add dynamic computation of margin based on overall range
                    if minimum == maximum:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum) + np.log10(1.1))
                            values_min.append(np.log10(minimum))

                            for limit in limits:
                                pe_for_limit[str(limit)].append(np.log10(minima_for_limits[str(limit)]))

                        else:
                            values_max.append(maximum + 1.1)
                            values_min.append(minimum)

                            for limit in limits:
                                pe_for_limit[str(limit)].append(minima_for_limits[str(limit)])
                    else:

                        if plotting_configuration.log:
                            values_max.append(np.log10(maximum))
                            values_min.append(np.log10(minimum))

                            for limit in limits:
                                pe_for_limit[str(limit)].append(np.log10(minima_for_limits[str(limit)]))

                        else:
                            values_max.append(maximum)
                            values_min.append(minimum)
                            for limit in limits:
                                pe_for_limit[str(limit)].append(minima_for_limits[str(limit)])
                

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
            # plt.ylim(bottom=-1, top=3) # type: ignore
            # plt.ylim(bottom=-0.5, top=0.5) # type: ignore
            # plt.ylim(bottom=0.6, top=1) # type: ignore
            # plt.ylim(bottom=-2, top=3) # type: ignore
            plt.ylim(bottom=-3, top=4) # type: ignore
            # plt.ylim(bottom=-1, top=4) # type: ignore
            # plt.ylim(bottom=0, top=4) # type: ignore

            # assemble plot
            # plt.title(f"{plotting_configuration.name} - {method} - Tuning Ranges", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.title(f"{plotting_configuration.name}", fontsize=plotting_configuration.fontsize) # type: ignore 
            plt.xlabel("Rewrites/Tuning Runs") # type: ignore
            plt.ylabel("Runtime (ms) log" if plotting_configuration.log else "Runtime (ms)") # type: ignore 
            # plt.ylim(10**-6, 10)
            # plt.bar(x=x, height=values_max, bottom=values_min, width=0.6, color=colors_values, label=f"Performance Range") # type: ignore


            x: List[int] = list(range(len(points_for_run)))

            for run in x:
                
                x_coordinates: list[int] = [run for _ in range(len(points_for_run[run]))]
                plt.scatter(x_coordinates, points_for_run[run], color='red', s=3)
                
            
            # add line for performance evolution
            
            for limit in limits:
                # print(f"limit: {limit}")
                pe: List[float] = []
                minimum: float = 0
                # print(f"len: {len(pe_for_limit[str(limit)])}")
                for value in pe_for_limit[str(limit)]:
                    minimum = value
                    break

                # create performance evolution 
                # warning: invalid values have the value: invalid_limit
                for value in pe_for_limit[str(limit)]:
                    # print(f"value: {value}")
                    if value < minimum:
                        minimum = value
                    pe.append(minimum)
                
                pe_x: List[int] = list(range(len(pe)))

                # plot performance evolution
                plt.plot(pe_x, # type: ignore
                        pe, 
                        alpha=0.5, 
                        #  color='#4EC4B0', # teal green 
                        #  color='#B0A64C', # mustard yellow 
                        # color='grey',
                        # color='#C44E52', # red 
                        # color='#FFD700',
                        lw=2, 
                        label=f"Tuning Budget: {str(limit)}"
                        ) 


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
                     label="Tuning Budget: 50"
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

            # plt.legend(loc='lower right', bbox_to_anchor=(1, 0.15)) # type: ignore
            # plt.legend(loc='lower right', bbox_to_anchor=(1, 0.9)) # type: ignore
            # plt.legend(loc='upper left', bbox_to_anchor=(0, -1))
            legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),fancybox=True, shadow=True, ncol=3)
            # legend = plt.legend()

            # Change the background color of the legend
            legend.get_frame().set_facecolor('lightgray')

            # Optionally, you can also set the edge color and linewidth
            legend.get_frame().set_edgecolor('black')
            legend.get_frame().set_linewidth(2)
            plt.tight_layout
            # plt.legend(loc='lower right') # type: ignore


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


