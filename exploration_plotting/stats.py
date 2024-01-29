#!/bin/python3.8

from .plotting_configuration import PlottingConfiguration

import csv

from . import util


def stats(plotting_configuration: PlottingConfiguration) -> None:
    data = util.get_data_fully(plotting_configuration)

    # TODO think about more metrics

    # process stats
    runs_stats = {}
    for method in data:
        run_counter = 0

        for run in data[method][1]:
            # samples
            samples = len(data[method][1][run])

            # tuning_runs/rewrites
            grouped_by_tuning = util.group_by_tuning(data[method][1][run])
            tuning_runs = len(grouped_by_tuning)

            # minimum & maximum
            numbers: List[float] = [float(elem['runtime']) for elem in data[method][1][run]]
            minimum = min(list(filter(lambda x: (x != -1), numbers)))
            maximum = max(list(filter(lambda x: (x != -1), numbers)))
            speedup = numbers[0] / minimum
            # speedup = plotting_configuration.default / minimum
            minimum_index = numbers.index(minimum)
            minimum_index_percent = (minimum_index / samples) * 100

            # duration
            start = float(data[method][1][run][0]['timestamp'])
            end = float(data[method][1][run][-1]['timestamp'])
            duration = (end - start) / 1000 / 60 / 60

            # invalids
            # len(list(filter([])))
            valid_samples = len([item for item in numbers if item != -1])
            valid_samples_fraction = valid_samples / len(numbers) * 100

            # if all samples of a tuning run are invalid, the rewrites is considered invalid
            invalid_rewrites = 0
            for group in grouped_by_tuning:
                invalid = [elem for elem in group if elem['error-level'] != 'None']
                if len(invalid) == len(group):
                    invalid_rewrites += 1

            valid_rewrites = tuning_runs - invalid_rewrites

            valid_rewrites_fraction = valid_rewrites / tuning_runs * 100

            # add stats
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
                maximum,
                f"{speedup:.2f}",
                minimum_index,
                f"{minimum_index_percent:.2f}"
            ]
            run_counter += 1

    # write runs_stats to file
    filename = f"{plotting_configuration.output}/{plotting_configuration.name}.csv"
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        header = [
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
            'maximum (ms)',
            'speedup total',
            'minimum after',
            'minimum after percent',
        ]
        csvwriter.writerow(header)

        for row in runs_stats:
            csvwriter.writerow(runs_stats[row])
