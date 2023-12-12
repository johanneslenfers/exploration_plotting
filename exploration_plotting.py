#!/bin/python3.8
from exploration_plotting.plotting_configuration import PlottingConfiguration
from exploration_plotting.scatter import scatter
from exploration_plotting.performance_evolution import performance_evolution
from exploration_plotting.facet import facet_plot
from exploration_plotting.speedup_tuning import speedup_tuning
from exploration_plotting.stats import stats

plots = {
    "scatter": scatter,
    "performance_evolution": performance_evolution,
    "facet": facet_plot,
    "speedup_tuning": speedup_tuning,
    "stats": stats,
}


def main():
    plot_config: PlottingConfiguration = PlottingConfiguration()
    plots[plot_config.plot](plot_config)


if __name__ == "__main__":
    main()
