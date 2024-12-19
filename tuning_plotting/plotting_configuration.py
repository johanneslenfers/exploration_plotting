#!/bin/python3.10
from typing import (
    Callable,
)

import argparse

# import plotting methods as static methods
from grouped_order_performance_evolution import grouped_order_performance_evolution
from order_ranges import order_ranges
from order_statistics import order_statistics

class PlottingConfiguration:
    """
    A class that encapsulates all the information required for plotting.
    """

    def __init__(self) -> None:

        # define parser 
        plotting_parser = argparse.ArgumentParser(description='Plotting Parser')
        plotting_parser.add_argument('-p', '--plot', choices=plotting_methods.keys(), help='Plotting Method', required=True)
        plotting_parser.add_argument('-i', '--input', help='Input Folder', required=True)
        plotting_parser.add_argument('-o', '--output', help='Output File')
        plotting_parser.add_argument('-l', '--log', action='store_true', help='Plot Log')
        plotting_parser.add_argument('-li', '--limit', type=int, help='Limit Plotting')
        plotting_parser.add_argument('-f', '--format', type=str, help='File format')

        # parse args and initialize variables     
        args: argparse.Namespace = plotting_parser.parse_args()

        # method, input, output 
        self.plotting_method: Callable[[PlottingConfiguration], None] = plotting_methods[args.plot]
        self.input: str = args.input
        output: str = args.output
        self.output: str = ""
        if not output:
            self.output = self.input
        else:
            self.output = output

        # parse name
        self.name = str(self.output).split('/')[-1]

        # parse optional arguments
        self.expert: float | None = args.expert
        self.default: float | None = args.default
        self.limit: int | None = args.limit
        self.format: str | None = args.format

        if args.format is not None:
            self.format = args.format
        else:
            self.format = 'pdf'

        self.log = False
        if args.log:
            self.log = True

        # constant arguments
        self.figsize: tuple[int, int] = (8, 8)
        self.dpi = 1000
        self.fontsize = 11

    def plot(self) -> None:
        self.plotting_method(self)
        pass

    def __str__(self) -> str:
        return f"""Plotting Configuration: 
        plotting_method: {self.plotting_method}
        name: {self.name}
        input: {self.input}
        output: {self.output}
        expert: {self.expert}
        default: {self.default}
        log: {self.log}
        limit: {self.limit}
        file_format: {self.format}
        """

# register plotting methods 
plotting_methods: dict[str, Callable[[PlottingConfiguration], None]]= {
    "grouped_order_performance_evolution": grouped_order_performance_evolution,
    "order_ranges": order_ranges,
    "order_statistics": order_statistics
}