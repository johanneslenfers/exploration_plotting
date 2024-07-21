#!/bin/python3.10
from __future__ import annotations

from typing import (
    List,
    Dict,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

import util
import csv

@staticmethod
def stats(plotting_configuration: PlottingConfiguration) -> None:
    exploration_data: util.ExplorationData = util.get_data_fully(plotting_configuration.input)

    # TODO think about more metrics

    # process stats
    runs_stats: Dict[str, List[str | int | float]] = {}
    for method in exploration_data:
        run_counter: int = 0

        for run in exploration_data[method][1]:
            # samples
            samples: int = len(exploration_data[method][1][run])

            # tuning_runs/rewrites
            grouped_by_tuning: List[List[Dict[str, str]]] = util.group_by_tuning(exploration_data[method][1][run])
            tuning_runs: int = len(grouped_by_tuning)

            # minimum & maximum
            numbers: List[float] = [float(elem['runtime']) for elem in exploration_data[method][1][run]]
            minimum: float = min(list(filter(lambda x: (x != -1), numbers)))
            maximum: float = max(list(filter(lambda x: (x != -1), numbers)))
            speedup: float = numbers[0] / minimum
            # speedup = plotting_configuration.default / minimum
            minimum_index: int = numbers.index(minimum)
            minimum_index_percent: float = (minimum_index / samples) * 100

            # duration
            start: float = float(exploration_data[method][1][run][0]['timestamp'])
            end: float = float(exploration_data[method][1][run][-1]['timestamp'])
            duration: float = (end - start) / 1000 / 60 / 60

            # invalids
            # len(list(filter([])))
            valid_samples: int = len([item for item in numbers if item != -1])
            valid_samples_fraction: float = valid_samples / len(numbers) * 100

            # if all samples of a tuning run are invalid, the rewrites is considered invalid
            invalid_rewrites: int = 0
            for group in grouped_by_tuning:
                invalid: List[Dict[str, str]] = [elem for elem in group if elem['error-level'] != 'None']
                if len(invalid) == len(group):
                    invalid_rewrites += 1

            valid_rewrites: int = tuning_runs - invalid_rewrites

            valid_rewrites_fraction: float = valid_rewrites / tuning_runs * 100

            # add stats
            # TODO fix GFLOP computation 
            runs_stats[f"{method}_{run}"] = [
                method,
                run_counter,
                samples,
                valid_samples,
                f"{valid_samples_fraction:.2f}",
                tuning_runs,
                valid_rewrites,
                f"{valid_rewrites_fraction:.2f}",
                f"{duration:.2f}",
                minimum,
                f"{util.get_gflops(minimum):.4f}",
                maximum,
                f"{util.get_gflops(maximum):.5}",
                f"{speedup:.2f}",
                minimum_index,
                f"{minimum_index_percent:.2f}"
            ]
            run_counter += 1

    # write runs_stats to file
    filename: str = f"{plotting_configuration.output}/{plotting_configuration.name}.csv"
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        header: List[str] = [
            'method',
            'run',
            'samples',
            'valid samples',
            'valid samples percent',
            'rewrites',
            'valid rewrites',
            'valid rewrites percent',
            'duration (h)',
            'minimum (ms)',
            'minimum (gflops)',
            'maximum (ms)',
            'maximum (gflops)',
            'speedup total',
            'minimum after',
            'minimum after percent',
        ]
        csvwriter.writerow(header)

        for row in runs_stats:
            csvwriter.writerow(runs_stats[row])
