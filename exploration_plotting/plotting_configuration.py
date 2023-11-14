#!/bin/python3.8
import argparse


class PlottingConfiguration:

    def __init__(self):
        plotting_parser = argparse.ArgumentParser(description='Plotting Parser')
        plotting_parser.add_argument('-p', '--plot',
                                     choices=['performance_evolution', 'scatter', 'facet', 'speedup_tuning'],
                                     help='Plotting Method',
                                     required=True)
        plotting_parser.add_argument('-i', '--input', help='Input Folder', required=True)
        plotting_parser.add_argument('-o', '--output', help='Output File')
        plotting_parser.add_argument('-e', '--expert', type=float, help='Expert Performance')
        plotting_parser.add_argument('-d', '--default', type=float, help='Default Performance')
        plotting_parser.add_argument('-l', '--log', action='store_true', help='Plot Log')
        plotting_parser.add_argument('-n', '--name', help='Give Name')

        args = plotting_parser.parse_args()

        self.plot: str = args.plot
        self.input: str = args.input

        # parse output
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

        self.log = False
        if args.log:
            self.log = True

        # constant arguments
        self.figsize = (10, 10)
        self.dpi = 1000
        self.fontsize = 22

    def __str__(self):
        return f"""Plotting Configuration: 
        plot: {self.plot}
        name: {self.name}
        input: {self.input}
        output: {self.output}
        expert: {self.expert}
        default: {self.default}
        log: {self.log}
        """
