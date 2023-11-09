#!/bin/python3.8
from exploration_plotting.plotting_configuration import PlottingConfiguration
from exploration_plotting.scatter import scatter
from exploration_plotting.performance_evolution import performance_evolution

plots = {
    "scatter": scatter,
    "performance_evolution": performance_evolution
}


def main():
    plot_config: PlottingConfiguration = PlottingConfiguration()
    plots[plot_config.plot](plot_config)


if __name__ == "__main__":
    main()
