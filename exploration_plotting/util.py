#!/bin/python3.10

from typing import(
    Dict,
    Tuple,
    List,
    Iterator,
)

import csv
import os

# alias for exploration data 
# improves readability for type annotations  
ExplorationDataRuntime = Dict[str, Tuple[int, Dict[str, List[Tuple[bool, float]]]]]
MethodDataRuntime = Dict[str, List[Tuple[bool, float]]]

ExplorationData = Dict[str, Tuple[int, Dict[str, List[Dict[str, str]]]]]
MethodData = Dict[str, List[Dict[str, str]]]



# global colors 
# TODO think about that 
colors: List[str] = [
    'tab:red',
    'tab:green',
    'tab:cyan',
    'tab:olive',
    'tab:purple',
    'tab:brown',
    'tab:pink',
    'tab:blue',
    'tab:orange',
    'tab:gray',
]

# helper method to sort the folders based on a timestamp   
@staticmethod
def pather(folder: Tuple[str, str]) -> float:
    return os.path.getmtime(folder[1])

# TODO make this a flexible module that can compute GFLOPS for various computations 
@staticmethod
def get_gflops(runtime: float) -> float:
    MatrixSize = 1024
    NumOps = 2 * MatrixSize ** 3
    gflops = 1.0e-9 * NumOps / runtime

    return gflops

@staticmethod
def get_data(input: str) -> ExplorationDataRuntime:

    # get sub folders from input folder
    folders: List[Tuple[str, str]] = [(f.name, f.path) for f in os.scandir(input) if f.is_dir()]

    # sort folders based on their generation time  
    folders = sorted(folders, key=pather, reverse=False)

    # get data from the sorted input folders
    data: ExplorationDataRuntime = {}

    # the corresponding list comprehension - hard to read 
    # data =  dict([(name, (counter, process_subfolder(path))) for (counter, (name, path)) in enumerate(folders)])

    # process data 
    counter: int = 0
    for (name, path) in folders:
        data[name] = (counter, process_subfolder(path))
        counter += 1

    return data


@staticmethod
def group_by_tuning(run: List[Dict[str, str]]) -> List[List[Dict[str, str]]]:

    # list of tuning runs 
    # each tuning run is a list of lines aka dictionary 
    grouped_by_tuning: List[List[Dict[str, str]]] = []
    group: List[Dict[str, str]] = []

    # low_level_hash: str = run[0]['low-level hash']
    rewrite_sequence: str = run[0]['rewrite']

    for line in run:
        # check if we have a new group
        # if low_level_hash != line['low-level hash'] and rewrite_sequence != line['rewrite']:
        if rewrite_sequence != line['rewrite']:
            # yes, update identifier
            # low_level_hash = line['low-level hash']
            rewrite_sequence = line['rewrite']

            # add elements to group
            grouped_by_tuning.append(group)

            # reset group
            group = []

        # otherwise add to group 
        group.append(line)

    
    grouped_by_tuning.append(group)

    return grouped_by_tuning


@staticmethod
def get_runtime_index(reader: Iterator[list[str]]) -> int:  

    # get header 
    header: List[str] = next(reader)

    # search for runtime in header
    runtime_index: int = 0
    counter: int = 0
    for elem in header:
        if ('runtime' in elem):
            runtime_index = counter
        counter += 1

    return runtime_index


@staticmethod
def process_subfolder(sub_folder: str) -> Dict[str, List[Tuple[bool, float]]]:
    files = os.listdir(sub_folder + "/" + "csv")

    fileData: Dict[str, List[Tuple[bool, float]]] = {}
    for f in files:
        if (f[-3:] == 'csv'):
            fileData[f] = process_file(sub_folder + "/" + "csv", f)

    return fileData


@staticmethod
def process_file(sub_folder: str, file: str) -> List[Tuple[bool, float]]:

    # prepare processing 
    ifd = open(str(sub_folder + '/' + file), mode='r')
    csv_reader = csv.reader(ifd, delimiter=',')
    runtime_index: int = get_runtime_index(csv_reader)
    line_count: int = 0
    data: List[Tuple[bool, float]] = []

    # process csv file 
    for row in csv_reader:
        # don't skip header
        if line_count == -1:
            # skip header
            line_count += 1
        else:
            line_count += 1

            if (str(row[runtime_index]) == '-1'):
                data.append((False, float(2147483647)))
            elif (str(row[runtime_index + 1]) == 'False'):
                data.append((False, float(2147483647)))
            else:
                data.append((True, float(row[runtime_index])))

    return data


@staticmethod
def get_data_fully(input: str) -> ExplorationData:

    # get sub folders from input folder
    folders: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(input) if f.is_dir()]
    folders = sorted(folders, key=pather, reverse=False)

    # get data from input folders
    data: ExplorationData = {}
    counter: int = 0
    for (name, path) in folders:
        data[name] = (counter, process_subfolder_fully(path))
        counter += 1

    return data


@staticmethod
def process_subfolder_fully(sub_folder: str) -> MethodData:
    files = os.listdir(sub_folder + "/" + "csv")

    fileData: MethodData = {}
    for f in files:
        if (f[-3:] == 'csv'):
            fileData[f] = process_file_fully(sub_folder + "/" + "csv", f)

    return fileData


@staticmethod
def process_file_fully(sub_folder: str, file: str) -> List[Dict[str, str]]:
    ifd = open(str(sub_folder + '/' + file), mode='r')

    csv_reader = csv.reader(ifd, delimiter=',')
    header = next(csv_reader)

    # create list of dicts
    data: List[Dict[str, str]] = []

    limiter = 0
    for line in csv_reader:
        limiter += 1

        # TODO check this 
        if limiter > 500000: 
            break
        entry_index = 0
        line_dict: Dict[str, str] = {}

        # TODO check what is going on here 
        for entry in header:
            # convert to float if possible?
            line_dict[entry] = line[entry_index]
            entry_index += 1

        data.append(line_dict)

    return data