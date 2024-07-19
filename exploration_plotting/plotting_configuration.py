#!/bin/python3.10
from typing import (
    Union,
    Callable,
    Dict
)

import argparse

# import plotting methods as static methods
from scatter import scatter
from scatter_pe import scatter_pe
from performance_evolution import performance_evolution
from speedup import speedup
from speedup_tuning import speedup_tuning
from stats import stats
from violin import violin
from all import all
from facet import facet_plot 


class PlottingConfiguration:
    """
    A class that encapsulates all the information required for plotting.
    """

    def __init__(self):

        # define parser 
        plotting_parser = argparse.ArgumentParser(description='Plotting Parser')
        plotting_parser.add_argument('-p', '--plot', choices=plotting_methods.keys(), help='Plotting Method', required=True)
        plotting_parser.add_argument('-i', '--input', help='Input Folder', required=True)
        plotting_parser.add_argument('-o', '--output', help='Output File')
        plotting_parser.add_argument('-e', '--expert', type=float, help='Expert Performance')
        plotting_parser.add_argument('-d', '--default', type=float, help='Default Performance')
        plotting_parser.add_argument('-l', '--log', action='store_true', help='Plot Log')
        plotting_parser.add_argument('-n', '--name', help='Give Name')
        plotting_parser.add_argument('-li', '--limit', type=int, help='Limit Plotting')
        plotting_parser.add_argument('-f', '--format', type=str, help='File format')
        plotting_parser.add_argument('-u', '--unit',
                                     choices=['runtime', 'gflops'],
                                     help='Unit ')


        # parse args and initialize variables     
        args = plotting_parser.parse_args()

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
        name: str = args.name
        self.name: str = ""
        if name:
            self.name = args.name
        else:
            self.name = str(self.output).split('/')[-1]

        # parse optional arguments
        self.expert: Union[float, None] = args.expert
        self.default: Union[float, None] = args.default
        self.limit: Union[int, None] = args.limit
        self.format: Union[str, None] = args.format

        if args.format is not None:
            self.format = args.format
        else:
            self.format = 'pdf'

        self.log = False
        if args.log:
            self.log = True

        if args.unit:
            self.unit: str = args.unit
        else:
            self.unit: str = "runtime"

        # constant arguments
        self.figsize = (10, 10)
        self.dpi = 1000
        self.fontsize = 22

    def plot(self):
        self.plotting_method(self)
        pass

    def __str__(self):
        return f"""Plotting Configuration: 
        plotting_method: {self.plotting_method}
        name: {self.name}
        input: {self.input}
        output: {self.output}
        expert: {self.expert}
        default: {self.default}
        log: {self.log}
        limit: {self.limit}
        unit: {self.unit}
        """

# register plotting methods 
plotting_methods: Dict[str, Callable[[PlottingConfiguration], None]]= {
    "scatter": scatter,
    "scatter_pe": scatter_pe,
    "performance_evolution": performance_evolution,
    "facet": facet_plot,
    "speedup_tuning": speedup_tuning,
    "speedup": speedup,
    "stats": stats,
    "violin": violin,
    "all": all,
}