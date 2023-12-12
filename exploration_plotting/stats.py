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
        print(f"method: {method}")
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
            minimum_index = numbers.index(minimum)
            minimum_index_percent = (minimum_index / samples) * 100

            # duration
            start = float(data[method][1][run][0]['timestamp'])
            end = float(data[method][1][run][-1]['timestamp'])
            duration = (end - start) / 1000 / 60 / 60

            # add stats
            runs_stats[run] = [
                method,
                run_counter,
                samples,
                tuning_runs,
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
            'rewrites',
            'duration (h)',
            'minimum (ms)',
            'maximum (ms)',
            'speedup total',
            'minimum after',
            'minimum after percent'
        ]
        csvwriter.writerow(header)

        for row in runs_stats:
            csvwriter.writerow(runs_stats[row])
