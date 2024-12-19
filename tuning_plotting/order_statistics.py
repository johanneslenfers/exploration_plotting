#!/bin/python3.10
from __future__ import annotations

import util
import csv
import numpy as np

from typing import (
    TYPE_CHECKING,
)


if TYPE_CHECKING:
    from plotting_configuration import PlottingConfiguration

@staticmethod
def order_statistics(plotting_configuration: PlottingConfiguration) -> None:

    experiment_data: util.ExperimentData = util.get_data(plotting_configuration.input)

    for benchmark in experiment_data:

        data: list[dict[str, int | float]] = []

        order_count: int = int(0)
        for order in experiment_data[benchmark]:

            # set default entries 
            order_entry: dict[str, int | float] = {}
            order_entry['order'] = order_count
            order_entry['default'] = get_default_performance(order)

            # compute entries with statistics for each method
            for method in order:

                tuning_runs_result: list[float] = [min([sample.runtime for sample in tuning_run]) for tuning_run in order[method]]

                order_entry[f"{method}_mean"] = round(float(np.mean(tuning_runs_result)), 2)
                order_entry[f"{method}_min"] = round(float(min(tuning_runs_result)), 2)
                order_entry[f"{method}_max"] = round(float(max(tuning_runs_result)), 2)
                order_entry[f"{method}_std"] = round(float(np.std(tuning_runs_result)), 2)

            data.append(order_entry)
            order_count += 1

        write_to_file(data=data, 
                      filename=f"{plotting_configuration.output}/{benchmark}_stats.csv"
                      )

    return None


def get_default_performance(data: util.OrderData) -> float:
    # TODO: what do do with taco where we don't have a default configuration?

    # try embedding_random_sampling as default method  
    try:
        tuning_run: util.TuningRun = data['embedding_random_sampling'][0]
        return tuning_run[0].runtime

    # otherwise take first method 
    except:
        tuning_run: util.TuningRun = data[list(data.keys())[0]][0]
        return tuning_run[0].runtime

def write_to_file(data: list[dict[str, int | float]], filename: str) -> None:

    # Open a file in write mode
    with open(filename, "w", newline="") as file:

        # Define fieldnames (keys from the dictionary)
        header: list[str] = list(data[0].keys())
        
        # Create a DictWriter object
        writer = csv.DictWriter(file, fieldnames=header) # type: ignore
        
        # Write the header row
        writer.writeheader() # type: ignore
        
        # Write the rows
        writer.writerows(data) # type: ignore

    return None