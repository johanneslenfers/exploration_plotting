#!/bin/python3.8
from exploration_plotting.plotting_configuration import PlottingConfiguration
from exploration_plotting.scatter import scatter
from exploration_plotting.performance_evolution import performance_evolution
from exploration_plotting.facet import facet_plot
from exploration_plotting.speedup_tuning import speedup_tuning
from exploration_plotting.speedup import speedup
from exploration_plotting.stats import stats
from exploration_plotting.violin import violin
from exploration_plotting.all import all

plots = {
    "scatter": scatter,
    "performance_evolution": performance_evolution,
    "facet": facet_plot,
    "speedup_tuning": speedup_tuning,
    "speedup": speedup,
    "stats": stats,
    "violin": violin,
    "all": all,
}


def main():
    # get configuration
    plot_config: PlottingConfiguration = PlottingConfiguration()

    # call plotting function with configuration
    plots[plot_config.plot](plot_config)


if __name__ == "__main__":
    main()
