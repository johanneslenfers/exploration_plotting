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

import util
from scipy.stats import sem # type: ignore
import math
import numpy as np
from matplotlib import pyplot as plt

@staticmethod
def tuning_budget_analysis(plotting_configuration: PlottingConfiguration) -> None:

    # get data an group by tuning runs 
    multiple_exploration_data: util.MultipleExplorationData = util.get_multiple_data_fully(plotting_configuration.input)

    plt.figure( # type: ignore
        figsize=(10, 10), 
        dpi=plotting_configuration.dpi
    )

    # assemble plot
    plt.title(f"Mean of relative Speedup of all Tuning runs", fontsize=plotting_configuration.fontsize) # type: ignore 
    plt.xlabel("Tuning Samples") # type: ignore
    plt.ylabel("Percentage of Total Speedup") # type: ignore 

    for exploration_data in multiple_exploration_data:
        for method in multiple_exploration_data[exploration_data]:
            # we do not assume multiple runs for the tuning budget analysis 
            # otherwise, plot as separate lines 
            for run in multiple_exploration_data[exploration_data][method][1]:

                # TODO: extract this automatically
                limits: List[int] = list(range(1, 51))

                grouped_by_tuning: List[List[Dict[str, str]]] = util.group_by_tuning(multiple_exploration_data[exploration_data][method][1][run])
                plot_average_speedup(grouped_by_tuning=grouped_by_tuning, limits=limits, name=f"{exploration_data}")

    # hline with 95 percent 
    plt.axhline(y=0.95, color='black', linestyle='-', label='95%', alpha=1, lw=2) # type: ignore 
    plt.legend() # type: ignore
    plt.savefig( # type: ignore
        f"{plotting_configuration.output}/{plotting_configuration.name}analysis.{plotting_configuration.format}",
        dpi=plotting_configuration.dpi)

    return None


@staticmethod
def plot_average_speedup(grouped_by_tuning: List[List[Dict[str, str]]], limits: List[int], name: str) -> None:

    avg_speedup_best: Dict[str, Tuple[float, float]] = get_average_speedup_of_all(
        grouped_by_tuning=grouped_by_tuning, 
        limits=limits, 
        )

    values: List[float] = [elem[0] for elem in avg_speedup_best.values()]
    values.insert(0, 0)
    limits.insert(0, 0)

    confidence: List[float] = [elem[1] for elem in avg_speedup_best.values()]
    confidence.insert(0, 0)

    # plot average speedup
    plt.plot( # type: ignore
        limits,
        values, 
        alpha=1, 
        lw=2,
        label=f"{name}"
        )

    # plot confidence interval
    lower: List[float] = []
    upper: List[float] = []
    for i in range(len(values)):
        lower.append(values[i] - confidence[i])
        upper.append(values[i] + confidence[i])

    plt.fill_between( # type: ignore
        limits, 
        lower, 
        upper, 
        alpha=0.2
        ) 

    return None


@staticmethod
def average_speedup(grouped_by_tuning: List[List[Dict[str, str]]], limit: int) -> float:

    speedups: List[float] = speedup_group(grouped_by_tuning, limit)
    return sum(speedups) / len(speedups)


@staticmethod
def speedup_group(grouped_by_tuning: List[List[Dict[str, str]]], limit: int) -> List[float]:

    speedups: List[float] = []  
    for group in grouped_by_tuning:

        # if group[0]'valid'] 
        if float(group[0]['runtime']) != -1:

            baseline: float = float(group[0]['runtime'])
            minimum: float = min(list(filter(lambda x: x != -1, [float(sample['runtime']) for sample in group[:limit]])))

            speedup: float = baseline / minimum
            speedups.append(speedup)

    return speedups

@staticmethod
def total_speedups(grouped_by_tuning: List[List[Dict[str, str]]], limits: List[int]) -> Dict[str, float]:
    return dict([(str(limit), math.prod(rs)) for limit, rs in [(limit, relevant_speedup(grouped_by_tuning, limit)) for limit in limits]])


@staticmethod
def relevant_speedup(grouped_by_tuning: List[List[Dict[str, str]]], limit: int) -> List[float]:
    # identify important rewrites/tuning runs 
    minimum: float = float(grouped_by_tuning[0][0]['runtime'])

    speedups_relevant: List[float] = []

    for group in grouped_by_tuning:

        # filter out invalid samples 
        filtered: list[float] = list(filter(lambda x: x != -1, [float(sample['runtime']) for sample in group[:limit]]))

        # check if we have valid samples
        if len(filtered) != 0:

            # check group is relevant (we find a new minimum) 
            if min(filtered) < minimum:

                old_min: float = minimum
                minimum = min(filtered)

                speedup: float = old_min / minimum
                speedups_relevant.append(speedup)
           
    return speedups_relevant

@staticmethod
def get_speedup_of_tuning_runs(grouped_by_tuning: List[List[Dict[str, str]]], limits: List[int]) -> List[Dict[int, float]]:

    # get baseline for speedup calculation  
    baseline: float = float(grouped_by_tuning[0][0]['runtime'])

    # first filter out all runs that are invalid 
    tuning_run_performance: List[List[float]] = []
    for group in grouped_by_tuning:
        tuning_run: List[float] = []
        for sample in group:
            tuning_run.append(float(sample['runtime']))
        tuning_run_performance.append(tuning_run)

    # filter all tuning runs that are completely invalid 
    tuning_run_performance: List[List[float]] = list(filter(lambda x: len(list(filter(lambda y: y != -1, x))), tuning_run_performance))

    # for each tuning run we have a dict with the speedup evolution as limits 
    speedup_group: List[Dict[int, float]] = []

    # convert to speedup evolution for each run 
    for run in tuning_run_performance:

        speedup_limit: Dict[int, float] = {}
        for limit in limits:

            if(len(list(filter(lambda x: x != -1.0, run))) > limit): 

                # get best of this run so far (for 100 percent speedup)
                base_min: float = baseline/min(list(filter(lambda x: x != -1.0, run)))

                if(len(list(filter(lambda x: x != -1.0, run[:limit])))) == 0:
                    speedup_limit[limit] = 0
                else:
                    # get minimum until current limit 
                    minimum: float = min(list(filter(lambda x: x != -1.0, run[:limit]))) 
                    speedup_limit[limit] = (baseline/minimum)/base_min

        if(len(speedup_limit)) > 0:
            speedup_group.append(speedup_limit)

    return speedup_group


@staticmethod
def get_average_speedup_of_all(grouped_by_tuning: List[List[Dict[str, str]]], limits: List[int]) -> Dict[str, Tuple[float, float]]:

    # get baseline for speedup calculation and best amount groups
    baseline: float = float(grouped_by_tuning[0][0]['runtime'])

    groups: List[List[float]] = [list(map(lambda x: float(x['runtime']), group)) for group in grouped_by_tuning]
    groups = list(filter(lambda x: len(list(filter(lambda y: y != -1, x))) > 0, groups))

    speedup_fraction: Dict[str, List[float]] = {}

    for limit in limits:

        speedup_limit: List[float] = []

        # get speedup until limit for each group 
        for group in groups:

            if len(list(filter(lambda x: x != -1, group[:limit]))) > 0:
                base_min: float = baseline/min(list(filter(lambda x: x != -1, group)))
                minimum: float = min(list(filter(lambda x: x != -1, group[:limit])))
                speedup_limit.append((baseline/minimum)/base_min)
            else:
                speedup_limit.append(0)

        speedup_fraction[str(limit)] = speedup_limit
        
    # compute average and confidence interval 
    averge_speedup_per_limit: Dict[str, Tuple[float, float]] = {}
    for limit in limits:
        averge_speedup_per_limit[str(limit)] = (
            float(np.mean(speedup_fraction[str(limit)])),
            sem(speedup_fraction[str(limit)]) * 1.96
            )

    return averge_speedup_per_limit


@staticmethod
def get_average_speedup_of_best(grouped_by_tuning: List[List[Dict[str, str]]], limits: List[int], amount: int) -> Dict[str, float]:

    # get baseline for speedup calculation and best amount groups
    baseline: float = float(grouped_by_tuning[0][0]['runtime'])
    best_groups: List[List[float]] = get_best_groups(grouped_by_tuning=grouped_by_tuning, amount=amount)

    speedup_fraction: Dict[str, List[float]] = {}

    for limit in limits:

        speedup_limit: List[float] = []

        # get speedup until limit for each group 
        for group in best_groups:

            if len(list(filter(lambda x: x != -1, group[:limit]))) > 0:
                base_min: float = baseline/min(list(filter(lambda x: x != -1, group)))
                minimum: float = min(list(filter(lambda x: x != -1, group[:limit])))
                speedup_limit.append((baseline/minimum)/base_min)
            else:
                speedup_limit.append(0)


        speedup_fraction[str(limit)] = speedup_limit
        
    # compute average 
    averge_speedup_per_limit: Dict[str, float] = {}
    for limit in limits:
        averge_speedup_per_limit[str(limit)] = sum(speedup_fraction[str(limit)])/len(speedup_fraction[str(limit)])

    return averge_speedup_per_limit



@staticmethod
def get_best_groups(grouped_by_tuning: List[List[Dict[str, str]]], amount: int) -> List[List[float]]:

    groups: List[Tuple[float, List[float]]] = [] 

    for group in grouped_by_tuning:

        # get runtimes only 
        group_runtimes: List[float] = ([float(sample['runtime']) for sample in group])

        if(len(list(filter(lambda x: x != -1, group_runtimes))) != 0):
            # get minimum of group
            minimum: float = min(list(filter(lambda x: x != -1, group_runtimes)))

            groups.append((minimum, group_runtimes))

    # sort by minium and extract the amount best groups 
    groups.sort(key=lambda x: x[0])
    groups = groups[:amount]

    # return only the runtimes 
    return [group[1] for group in groups]
