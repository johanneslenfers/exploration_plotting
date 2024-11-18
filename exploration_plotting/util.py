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
RunDataRuntime = List[Tuple[bool, float]]
TuningRunDataRuntime = List[Dict[str, str]]
MethodDataRuntime = Dict[str, RunDataRuntime]
ExplorationDataRuntime = Dict[str, Tuple[int, MethodDataRuntime]]
MultipleExplorationDataRuntime = Dict[str, ExplorationDataRuntime]

RunData = List[Dict[str, str]]
TuningRunData = List[Dict[str, str]]
MethodData = Dict[str, RunData]
ExplorationData = Dict[str, Tuple[int, MethodData]]
MultipleExplorationData = Dict[str, ExplorationData]

# name map
names_map: Dict[str, str] = {
    # benchmarks
    "acoustic" : "Acoustic",
    "asum" : "Asum",
    "kmeans" : "KMeans",
    "mm" : "MM",
    "mm_2070" : "MM (RTX 2070)",
    "scal" : "Scal",

    # Methods
    "MCTS": "MCTS",
    "Exhaustive" : "Breadh-First-Search",
    "RandomGraph" : "Random Sampling",
    "LocalSearch" : "Local Search",

    # Methods 2
    "MCTS_adjusted": "MCTS: Adj. Tuning-Budget",
    "Exhaustive_adjusted" : "Breadh-First-Search: Adj. Tuning-Budget",
    "RandomGraph_adjusted" : "Random Sampling: Adj. Tuning-Budget",
    "LocalSearch_adjusted" : "Local Search: Adj. Tuning-Budget",
}

tuning_budget_map: Dict[str, str] = {
    "acoustic" : "10",
    "asum" : "35",
    "kmeans" : "10",
    "mm" : "10",
    "mm_2070" : "10",
    "scal" : "25",
}


# global colors 
# TODO think about that 
colors2: List[str] = [
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

bottom_top: Dict[str, Tuple[float, float]] = {
    "acoustic" : (0.01, 120),
    "asum" : (0.005, 1000),
    "kmeans" : (0.01, 10000),
    "mm" : (1, 10000),
    "mm_2070" : (1, 10000),
    "scal" : (0.1, 10000),
}

left_right: Dict[str, Tuple[float, float]] = {
    "acoustic" : (0,  50000), # or max 
    "asum" : (0, 5000),
    "kmeans" : (0, 15000),
    "mm" : (0, 25000),
    "mm_2070" : (0, 50000),
    "scal" : (0, 5000),
}                                   

colors: List[str] = [
    '#1f77b4', # blue 
    '#ff7f0e', # orange 
    '#2ca02c', # green 
    '#d62728', # red 
    '#e377c2', # coral
    '#2ca02c', # bright teal 
    'tab:gray', # gray
    '#fdae61', # soft yellow
    'black', # black 

    # back up colors 
    # '#ff6f61',
    # '#2ca02c', # bright teal
    # '#ff7f0e', # orange
    # '#1a5e92', # darker blue 
    # '#3b6aa0', # grayish blue
    # '#4a90d9', # lighter blue
    # '#3b6aa0', # grayish blue 
    # '#5a9bd4', # muted blue 
    # '#1f77b4', # standard blue 
]

# helper method to sort the folders based on a timestamp   
@staticmethod
def pather(folder: Tuple[str, str]) -> float:
    return os.path.getmtime(folder[1])

# TODO make this a flexible module that can compute GFLOPS for various computations 
@staticmethod
def get_gflops(runtime: float) -> float:
    MatrixSize = 1024
    NumOps: int = 2 * MatrixSize ** 3
    gflops: float = 1.0e-9 * NumOps / runtime

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
def group_by_tuning(run: RunData) -> List[RunData]:

    # list of tuning runs 
    # each tuning run is a list of lines aka dictionary 
    grouped_by_tuning: List[RunData] = []
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
    files: List[str] = os.listdir(sub_folder + "/" + "csv")

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
def get_multiple_data(input: str) -> MultipleExplorationDataRuntime:

    # for each exploration folder in the input folder
    explorations: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(input) if f.is_dir()]
    explorations = sorted(explorations, key=pather, reverse=False)
    multiple_data: MultipleExplorationDataRuntime = {}

    for exploration in explorations:

        # get sub folders from parent folder 
        folders: list[tuple[str, str]] = [(f.name, f"{f.path}") for f in os.scandir(f"{input}/{exploration[0]}") if f.is_dir()]
        folders = sorted(folders, key=pather, reverse=False)

        # get data from input folders
        data: ExplorationDataRuntime = {}
        counter: int = 0
        for (name, path) in folders:
            data[name] = (counter, process_subfolder(path))
            counter += 1

        multiple_data[exploration[0]] = data 

    return multiple_data


@staticmethod
def get_multiple_data_fully_filled(input: str) -> MultipleExplorationData:

    multiple_exploration_data: MultipleExplorationData = get_multiple_data_fully(input)

    # multiple_exploration_data_runtime: MultipleExplorationDataRuntime = {}

    for benchmark in multiple_exploration_data:
        for method in multiple_exploration_data[benchmark]:
            for run in multiple_exploration_data[benchmark][method][1]:
                grouped_by_tuning: List[RunData] = group_by_tuning(multiple_exploration_data[benchmark][method][1][run])
                filled_samples: RunData = fill_up(grouped_by_tuning, 50)

                multiple_exploration_data[benchmark][method][1][run] = filled_samples

    return multiple_exploration_data


@staticmethod
def fill_up(tuning_runs: List[RunData], length: int) -> RunData:

    tuning_runs_filled: RunData = []


    for tuning_run in tuning_runs:

        # print(f"Length: {len(tuning_run)}")

        tuning_run2: RunData = tuning_run.copy()

        # check if we need to fill up
        if(len(tuning_run) < length):
            print(f"Fill up: {len(tuning_run)}")
            for _ in range(len(tuning_run), length):
                # print("Fill up")
                tuning_run2.append(tuning_run[-1]) 

        # add filled tuning run to list
        for sample in tuning_run2:
            tuning_runs_filled.append(sample)

    length_total: int = 0
    for tuning_run in tuning_runs:
        length_total += len(tuning_run)

    print(f"Length: {length_total}")
    print(f"Length filled: {len(tuning_runs_filled)}")

    return tuning_runs_filled


@staticmethod
def get_multiple_data_fully(input: str) -> MultipleExplorationData:

    # for each exploration folder in the input folder
    explorations: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(input) if f.is_dir()]
    explorations = sorted(explorations, key=pather, reverse=False)

    multiple_data: MultipleExplorationData = {}

    for exploration in explorations:

        # get sub folders from parent folder 
        folders: list[tuple[str, str]] = [(f.name, f"{f.path}") for f in os.scandir(f"{input}/{exploration[0]}") if f.is_dir()]
        folders = sorted(folders, key=pather, reverse=False)

        # get data from input folders
        data: ExplorationData = {}
        counter: int = 0
        for (name, path) in folders:
            data[name] = (counter, process_subfolder_fully(path))
            counter += 1

        multiple_data[exploration[0]] = data 

    return multiple_data

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
    files: list[str] = os.listdir(sub_folder + "/" + "csv")
    files = sorted(files, reverse=False)

    fileData: MethodData = {}
    for f in files:
        if (f[-3:] == 'csv'):
            fileData[f] = process_file_fully(sub_folder + "/" + "csv", f)

    return fileData


@staticmethod
def process_file_fully(sub_folder: str, file: str) -> List[Dict[str, str]]:
    ifd = open(str(sub_folder + '/' + file), mode='r')

    csv_reader = csv.reader(ifd, delimiter=',')
    header: list[str]= next(csv_reader)

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

