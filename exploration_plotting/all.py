from .plotting_configuration import PlottingConfiguration
from .scatter import scatter
from .performance_evolution import performance_evolution
from .stats import stats


def all(plotting_configuration: PlottingConfiguration) -> None:
    scatter(plotting_configuration)
    performance_evolution(plotting_configuration)
    stats(plotting_configuration)
