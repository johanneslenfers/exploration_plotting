#!/bin/python3.10
from __future__ import annotations

from typing import (
    List,
    Dict,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

import util

from matplotlib import pyplot as plt
from matplotlib.ticker import LogFormatter

import numpy as np

# plt.style.use('seaborn-v0_8-darkgrid')

@staticmethod
def speedup_stacking(plotting_configuration: PlottingConfiguration) -> None:
    speedup_stacking_rewriting_and_tuning(plotting_configuration=plotting_configuration)
    speedup_stacking_tuning_only(plotting_configuration=plotting_configuration)

    return None


bar_colors: Dict[str, str] = {
    # 'to': '#3b6aa0',
    # 'to': '#e377c2', # coral
    # 'to': '#2ca02c',
    # 'to': '#fdae61', # soft yellow
    # 'to': '#1a5e92', # darker blue 
    # 'to': '#4a90d9', # lighter blue
    # 'to': '#3b6aa0', # grayish blue 
    # 'to': '#2ca02c', # bright teal 
    'to': 'grey', 
    'rw': '#5a9bd4', # muted blue 
    'rh': '#1f77b4', # standard blue 
    't': '#ff7f0e' # orange
}


@staticmethod
def speedup_stacking_rewriting_and_tuning(plotting_configuration: PlottingConfiguration) -> None:

    # get data an group by tuning runs 
    multiple_exploration_data: util.MultipleExplorationData = util.get_multiple_data_fully(plotting_configuration.input)

    plt.clf()
    plt.figure( # type: ignore
        figsize=(8, 4), 
        dpi=plotting_configuration.dpi
    )

    # y-axis log scale
    fig, ax = plt.subplots(figsize=(8, 4)) # type: ignore

    # assemble plot
    plt.ylabel("Speedup over Baseline") # type: ignore 
    plt.ylim(bottom=1, top=13000) # type: ignore

    benchmarks: List[str] = []
    speedups_rewriting_worst: List[float] = [] 
    speedups_rewriting: List[float] = [] 
    speedups_tuning: List[float] = [] 
    speedup_tuning_only: List[float] = []

    benchmark_keys: List[str] = sorted(multiple_exploration_data.keys())

    for benchmark in benchmark_keys:
        method: str = 'Exhaustive'
        # for method in multiple_exploration_data[benchmark]:
        # we do not assume multiple runs for this bar plots 
        for run in multiple_exploration_data[benchmark][method][1]:

            benchmarks.append(f"{benchmark}")

            grouped_by_tuning: List[List[Dict[str, str]]] = util.group_by_tuning(multiple_exploration_data[benchmark][method][1][run])

            # get tuning only speedup 
            baseline_group: List[Dict[str, str]] = grouped_by_tuning[0]
            baseline_tuning_run: List[float] = [float(sample['runtime']) for sample in baseline_group]
            baseline: float = get_first_valid_elem(baseline_tuning_run)
            minimum: float = min(list(filter(lambda sample: sample != -1, baseline_tuning_run)))
            speedup_tuning_only.append(baseline / minimum)

            bounds_min_max: List[Dict[str, float]] = []
            bounds_first_valid_min: List[Dict[str, float]] = []

            # get runtime only
            # and filter all tuning runs that are completely invalid 
            tuning_runs: List[List[float]] = []
            for group in grouped_by_tuning:
                tuning_run: List[float] = []
                for sample in group:
                    tuning_run.append(float(sample['runtime']))
                tuning_runs.append(tuning_run)

            tuning_runs = list(filter(lambda run: len(list(filter(lambda sample: sample != -1, run))), tuning_runs))

            # get baseline
            baseline: float = get_first_valid_elem(tuning_runs[0])

            # plot only best X tuning runs 
            # tuning_runs = get_best_tuning_runs(tuning_runs, 10)

            # get min max for each tuning run 
            for tuning_run in tuning_runs:
                bounds_min_max.append(get_min_max(tuning_run))

            for tuning_run in tuning_runs:
                bounds_first_valid_min.append(get_first_valid_max(tuning_run))


            # mean speedup for this method 
            mean_speedup_rewriting_worst: float = float(np.mean([baseline / bound['rewriting'] for bound in bounds_min_max]))
            mean_speedup_rewriting: float = float(np.mean([baseline / bound['rewriting'] for bound in bounds_first_valid_min]))
            mean_speedup_tuning: float = float(np.mean([baseline / bound['tuning'] for bound in bounds_first_valid_min]))

            # append to speedups 
            speedups_rewriting_worst.append(mean_speedup_rewriting_worst)
            speedups_rewriting.append(mean_speedup_rewriting)
            speedups_tuning.append(mean_speedup_tuning)

    x_pos = np.arange(len(benchmarks)) # type: ignore
    width: float = 0.45

    # plot speedups
    ax.bar(x_pos - width/2, speedup_tuning_only, width=width, label='Tuning Only', color=bar_colors['to'], alpha=1) # type: ignore

    ax.bar(x_pos + width/2, speedups_rewriting_worst, width=width, label='Rewriting Only (Lowest)', color=bar_colors['rw'], alpha=1) # type: ignore
    ax.bar(x_pos + width/2, speedups_rewriting, width=width, bottom=speedups_rewriting_worst, label='Rewriting Only (Heuristic)', color=bar_colors['rh']) # type: ignore

    ax.bar(x_pos + width/2, speedups_tuning, width=width, bottom=speedups_rewriting, label='Rewriting & Tuning', color=bar_colors['t']) # type: ignore

    # Adding numbers on top of the bars
    for i, speedups in enumerate(zip(speedup_tuning_only, speedups_tuning)):

        fraction_tuning_only: float = np.log10(speedups[0])/np.log10(speedups[1])

        # fraction_tuning_only: float = speedups[0]/speedups[1]
        if((speedups[0] - (0.15 *speedups[0])) < 1.4):
            ax.text(i - width/2, speedups[0] + 0.1, f"{fraction_tuning_only:.2%}", ha='center', va='bottom', fontweight="bold")  # type: ignore
        else:
            ax.text(i - width/2, speedups[0] - (0.15 *  speedups[0]), f"{fraction_tuning_only:.2%}", ha='center', va='top', fontweight="bold")  # type: ignore

    # Adding numbers on top of the bars
    for i, speedups in enumerate(zip(speedups_rewriting_worst, speedups_rewriting, speedups_tuning)):

        # compute percentage 
        # 100% speedup is speedups[2]
        # fraction 1 is speedup[1]
        # fraction 2 is speedup[1]

        fraction_rewriting_worst: float = np.log10(speedups[0])/np.log10(speedups[2])
        fraction_rewriting: float = np.log10(speedups[1])/np.log10(speedups[2])

        if((speedups[0] - (0.15 *speedups[0])) < 1):
            ax.text(i + width/2, speedups[0] + 0.15, f"{fraction_rewriting_worst:.2%}", color='white', ha='center', va='bottom', fontweight="bold")  # type: ignore
        else:
            ax.text(i + width/2, speedups[0] - (0.15 *  speedups[0]), f"{fraction_rewriting_worst:.2%}", color='white', ha='center', va='top', fontweight="bold")  # type: ignore
        ax.text(i + width/2, speedups[0] + speedups[1] - (0.15 * speedups[1]), f"{fraction_rewriting:.2%}", color='white', ha='center', va='top', fontweight="bold")  # type: ignore
        # ax.text(i + width/2, speedups[0] + speedups[1] + speedups[2] - (0.15*speedups[2]), f"{1:.2%}", color='white', ha='center', va='top', fontweight="bold")  # type: ignore
        ax.text(i + width/2, speedups[0] + speedups[1] + speedups[2] - (0.15*speedups[2]), f"{1:.2%}", color='black', ha='center', va='top', fontweight="bold")  # type: ignore

    # complete 
    # hline with 95 percent 
    # plt.axhline(y=0.95, color='black', linestyle='-', label='95%', alpha=1, lw=2) # type: ignore 

    ax.set_xticks(x_pos) # type: ignore
    ax.set_xticklabels([util.names_map[benchmark] for benchmark in benchmarks], fontweight="bold")  # type: ignore

    ax.grid(visible=False, axis='x') # type: ignore
    ax.grid(visible=True, axis='y', linestyle='-', color='white') # type: ignore

    # y-axis log scale 
    ax.set_yscale('log') # type: ignore 
    
    # Use LogFormatter to show the actual values
    ax.yaxis.set_major_formatter(LogFormatter()) # type: ignore

    # from matplotlib.text import Text
    # from matplotlib.lines import Line2D
    handles, labels = ax.get_legend_handles_labels() # type: ignore
    legend = plt.legend(handles=handles, labels=labels) # type: ignore

    legend.get_frame().set_visible(True) # type: ignore
    legend.get_frame().set_facecolor("white")  # Set the frame face color to white # type: ignore
    legend.get_frame().set_edgecolor("black")  # Set the border color # type: ignore
    legend.get_frame().set_linewidth(1.5)      # Set the border line width # type: ignore

    plt.tight_layout() # type: ignore

    log_appendix: str = ""
    if plotting_configuration.log:
        log_appendix = "_log"
    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}_relative{log_appendix}.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)

    return None


@staticmethod
def speedup_stacking_tuning_only(plotting_configuration: PlottingConfiguration) -> None:


    # get data an group by tuning runs 
    multiple_exploration_data: util.MultipleExplorationData = util.get_multiple_data_fully(plotting_configuration.input)

    plt.clf()
    plt.figure( # type: ignore
        figsize=(8, 5), 
        dpi=plotting_configuration.dpi
    )

    # y-axis log scale
    fig, ax = plt.subplots(figsize=(8, 5)) # type: ignore

    # assemble plot
    plt.ylabel("Speedup over Baseline achieved by tuning only") # type: ignore 
    plt.ylim(bottom=1, top=13000) # type: ignore

    benchmarks: List[str] = []
    speedups: List[float] = []
    for benchmark in multiple_exploration_data:
        for method in multiple_exploration_data[benchmark]:
            # we do not assume multiple runs for this bar plots 
            for run in multiple_exploration_data[benchmark][method][1]:

                benchmarks.append(f"{benchmark}")

                grouped_by_tuning: List[List[Dict[str, str]]] = util.group_by_tuning(multiple_exploration_data[benchmark][method][1][run])

                # get first tuning run 
                baseline_group: List[Dict[str, str]] = grouped_by_tuning[0]
                baseline_tuning_run: List[float] = [float(sample['runtime']) for sample in baseline_group]

                # get min that is not -1 

                # bounds_min_max: List[Dict[str, float]] = []
                # bounds_first_valid_min: List[Dict[str, float]] = []

                # get baseline
                baseline: float = get_first_valid_elem(baseline_tuning_run)
                minimum: float = min(list(filter(lambda sample: sample != -1, baseline_tuning_run)))
                speedups.append(baseline / minimum)

    # plot speedups
    ax.bar(benchmarks, speedups, label='Speedup Parameter Tuning', color='#1f77b4', alpha=1) # type: ignore

    # y-axis log scale 
    ax.set_yscale('log') # type: ignore 
    
    # Use LogFormatter to show the actual values
    ax.yaxis.set_major_formatter(LogFormatter()) # type: ignore

    plt.legend() # type: ignore

    log_appendix: str = ""
    if plotting_configuration.log:
        log_appendix = "_log"
    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}_tuning_only{log_appendix}.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)

    return None


@staticmethod
def get_best_tuning_runs(tuning_runs: List[List[float]], amount: int) -> List[List[float]]:
    # sort tuning runs by runtime and only return x best 
    return sorted(tuning_runs, key=lambda run: min(list(filter(lambda sample: sample != -1, run))))[:amount]


@staticmethod
def get_first_valid_max(tuning_run: List[float]) -> Dict[str, float]:

    first_valid: float = get_first_valid_elem(tuning_run)
    minimum: float = min(list(filter(lambda sample: sample != -1, tuning_run)))

    return {'rewriting': first_valid, 'tuning': minimum}


@staticmethod
def get_min_max(tuning_run: List[float]) -> Dict[str, float]:

    minimum: float = min(list(filter(lambda sample: sample != -1, tuning_run)))
    maximum: float = max(list(filter(lambda sample: sample != -1, tuning_run)))

    return {'rewriting': maximum, 'tuning': minimum}


@staticmethod
def get_first_valid_elem(tuning_run: List[float]) -> float:

    for sample in tuning_run:
        if(sample != -1):
            return sample
    return -1


