#!/bin/python3.8

import csv
import os
import sys

from .plotting_configuration import PlottingConfiguration


def pather(folder):
    return os.path.getmtime(folder[1])


def get_gflops(runtime: float) -> float:
    MatrixSize = 1024
    NumOps = 2 * MatrixSize ** 3
    gflops = 1.0e-9 * NumOps / runtime

    return gflops


def get_data(plotting_configuration: PlottingConfiguration):
    # dict[str, tuple[int, dict[str, list[tuple[bool, float]]]]]:

    # get sub folders from input folder
    folders: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(plotting_configuration.input) if f.is_dir()]
    folders = sorted(folders, key=pather, reverse=False)

    # get data from input folders
    data: dict[str, tuple[int, dict[str, list[tuple[bool, float]]]]] = {}
    counter: int = 0
    for (name, path) in folders:
        data[name] = (counter, process_subfolder(path))
        counter += 1

    return data


def get_data_fully(plotting_configuration: PlottingConfiguration):
    # dict[str, tuple[int, dict[str, list[tuple[bool, float]]]]]:

    # get sub folders from input folder
    folders: list[tuple[str, str]] = [(f.name, f.path) for f in os.scandir(plotting_configuration.input) if f.is_dir()]
    folders = sorted(folders, key=pather, reverse=False)

    # get data from input folders
    data: dict[str, tuple[int, dict[str, list[tuple[bool, float]]]]] = {}
    counter: int = 0
    for (name, path) in folders:
        data[name] = (counter, process_subfolder_fully(path))
        counter += 1

    return data


def group_by_tuning(run):
    grouped_by_tuning = []
    group = []
    low_level_hash = run[0]['low-level hash']
    rewrite_sequence = run[0]['rewrite']
    for line in run:
        # check if we have a new group
        # if low_level_hash != line['low-level hash'] and rewrite_sequence != line['rewrite']:
        if rewrite_sequence != line['rewrite']:
            # yes, update identifier
            low_level_hash = line['low-level hash']
            rewrite_sequence = line['rewrite']

            # add elements to group
            grouped_by_tuning.append(group)

            # reset group
            group = []

        group.append(line)

    grouped_by_tuning.append(group)

    return grouped_by_tuning


def get_runtime_index(reader):
    # get header
    header = None
    for row in reader:
        header = row
        break

    # search for runtime in header
    runtime_index: int = 0
    counter: int = 0
    for elem in header:
        if ('runtime' in elem):
            runtime_index = counter
        counter += 1

    return runtime_index


def process_subfolder_fully(sub_folder: str):
    files = os.listdir(sub_folder + "/" + "csv")

    fileData = {}
    for f in files:
        if (f[-3:] == 'csv'):
            fileData[f] = process_file_fully(sub_folder + "/" + "csv", f)

    return fileData


def process_subfolder(sub_folder: str):
    files = os.listdir(sub_folder + "/" + "csv")

    fileData = {}
    for f in files:
        if (f[-3:] == 'csv'):
            fileData[f] = process_file(sub_folder + "/" + "csv", f)

    return fileData


def process_file_fully(sub_folder: str, file: str):
    ifd = open(str(sub_folder + '/' + file), mode='r')

    csv_reader = csv.reader(ifd, delimiter=',')
    header = next(csv_reader)

    # create list of dicts
    data: List[dict[str, str]] = []

    limiter = 0
    for line in csv_reader:
        limiter += 1
        if limiter > 500000:
            break
        entry_index = 0
        line_dict = {}
        for entry in header:
            # convert to float if possible?
            line_dict[entry] = line[entry_index]
            entry_index += 1
        data.append(line_dict)

    return data


def process_file(sub_folder: str, file: str):
    ifd = open(str(sub_folder + '/' + file), mode='r')

    csv_reader = csv.reader(ifd, delimiter=',')
    runtime_index = get_runtime_index(csv_reader)

    line_count = 0

    data = []

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
