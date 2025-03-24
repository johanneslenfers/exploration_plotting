#!/bin/python3.10
from dataclasses import dataclass

import csv
import os
import re
import ast

import numpy as np

ParameterConfiguration = dict[str, float | tuple[float]]

@dataclass
class TuningSample:
    parameter_configuration: ParameterConfiguration
    runtime: float # validity is encapsulated here
    timestamp: float

# this is a full csv file 
TuningRun = list[TuningSample]

# this represents all repitions for a method 
MethodData = list[TuningRun] 

# this represents all methods for an order 
OrderData = dict[str, MethodData]

# this represents all orders for a benchmark
BenchmarkData = list[OrderData] 

# this rerpesents all benchmarks for an experiment
ExperimentData = dict[str, BenchmarkData]

# helper method to sort the folders based on a timestamp   
@staticmethod
def pather(folder: tuple[str, str]) -> float:
    return os.path.getmtime(folder[1])


@staticmethod
def get_data(input: str) -> ExperimentData:

    # get sub folders from input folder
    folders: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(input) if f.is_dir()]

    # sort folders based on their generation time  
    folders = sorted(folders, key=pather, reverse=False)

    # process experiment data 
    experiment_data: ExperimentData = {}
    counter: int = 0
    for (benchmark_name, benchmark_path) in folders:
        experiment_data[benchmark_name] = process_benchmark_folder(benchmark_path)
        counter += 1

    return experiment_data


@staticmethod
def process_benchmark_folder(benchmark_folder: str) -> BenchmarkData:

    # print(f"    benchmark: {benchmark_folder}")

    benchmark_data: BenchmarkData = []

    # get order subfolders from input folder
    order_folders: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(benchmark_folder) if f.is_dir()]

    # sort folders based on their generation time  
    order_folders = sorted(order_folders, key=pather, reverse=False)

    # process data 
    for (_, order_path) in order_folders:
        benchmark_data.append(process_order_folder(order_path))

    return benchmark_data


@staticmethod
def process_order_folder(order_folder: str) -> OrderData:

    # print(f"        order: {order_folder}")

    order_data: OrderData = {}

    # get order subfolders from input folder
    method_folders: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(order_folder) if f.is_dir()]

    # sort folders based on their generation time  
    method_folders = sorted(method_folders, key=pather, reverse=False)

    # process data 
    for (method_name, method_path) in method_folders:
        order_data[method_name] = process_method_folder(method_path)

    return order_data


@staticmethod
def process_method_folder(method_folder: str) -> MethodData:

    method_data: MethodData = []

    # process files 
    files: list[str] = os.listdir(method_folder + "/" + "csv")
    for f in files:
        if (f[-3:] == 'csv'):
            method_data.append(process_tuning_run(method_folder + "/" + "csv", f))

    return method_data


@staticmethod
def process_tuning_run(tuning_run: str, file: str) -> TuningRun:

    # prepare processing 
    ifd = open(str(tuning_run + '/' + file), mode='r') # type: ignore
    csv_reader = csv.reader(ifd, delimiter=',')
    header: list[str] = next(csv_reader)
    runtime_index: int = get_runtime_index(header)

    # process csv file 
    line_count: int = 0
    data: TuningRun = []
    for row in csv_reader:
        # don't skip header
        if line_count == -1:
            # skip header
            line_count += 1
        else:
            line_count += 1

            # get parameter config
            parameter_configuration: ParameterConfiguration = {}
            for param in range(len(row[:-2])):


                # if parameter entry is written as tensor 
                if "tensor" in row[param]:
                    number: float = float(re.search(r'\d+\.?\d*', row[param]).group()) # type: ignore
                    parameter_configuration[header[param]] = number
                
                # if parameter entry is a permutation
                elif "(" in row[param][0]:
                    perm: tuple[float] = ast.literal_eval(row[param])
                    parameter_configuration[header[param]] = perm
                
                else: 
                    parameter_configuration[header[param]] = float(row[param])

            # process runtimes 
            if (str(row[runtime_index]) == '-1'):
                data.append(TuningSample(
                    parameter_configuration=parameter_configuration,
                    runtime=float(2147483647),
                    timestamp=float(row[-1])
                ))

            elif (str(row[runtime_index + 1]) == 'False'):
                data.append(TuningSample(
                    parameter_configuration=parameter_configuration,
                    runtime=float(2147483647),
                    timestamp=float(row[-1])
                ))
                
            else:
                data.append(TuningSample(
                    parameter_configuration=parameter_configuration,
                    runtime=float(row[runtime_index]),
                    timestamp=float(row[-1])
                ))

    return data


@staticmethod
def get_runtime_index(header: list[str]) -> int:  

    # search for runtime in header
    runtime_index: int = 0
    counter: int = 0
    for elem in header:
        if ('runtime' in elem):
            runtime_index = counter
        counter += 1

    return runtime_index


@staticmethod
# Custom formatter function
def log_formatter(value, tick_number): # type: ignore

    if float(value) <= 0.001: # type: ignore
        return f"{value:.3f}"  
    elif float(value) <= 0.01: # type: ignore
        return f"{value:.2f}"
    elif float(value) <= 0.1:  # type: ignore
        return f"{value:.1f}"  
    else:
        return f"{value:.0f}" 

@staticmethod
def get_global_range(benchmark_data: BenchmarkData) -> tuple[float, float]: 

    minimum: float = float('inf')
    maximum: float = 0.0

    for order in benchmark_data:
        for method in order:

            # collect min and max for all tuning runs for this method
            method_performance_min: list[float] = []
            method_performance_max: list[float] = []
            for tuning_run in order[method]:
                # get min/max for this tuning run 
                method_performance_min.append(min([sample.runtime for sample in tuning_run]))
                # for performance evolution we need the first default configuration, which might be better than the worst
                method_performance_max.append(tuning_run[0].runtime)

            # compare if mean of min/max is the new global min/max
            if(np.mean(method_performance_min)) < minimum:
                minimum = float(np.mean(method_performance_min))
            
            if(np.mean(method_performance_max)) > maximum:
                maximum = float(np.mean(method_performance_max))

    return (minimum, maximum)
