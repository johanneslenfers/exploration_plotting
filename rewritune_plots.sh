#!/bin/bash

# RQ1: The best optimization/rewriting method 

# Figure 4
python exploration_plotting/exploration_plotting.py -p performance_evolution_grouped -i /Users/jo/development/rise-lang/shine/experiments/exploration/results -n full_budget -f pdf 


# RQ2: 

# Figure 5
# tuning budget analysis
python exploration_plotting/exploration_plotting.py -p tuning_budget_analysis -i /Users/jo/development/rise-lang/shine/experiments/exploration/results -n tuning_budget_analysis -f pdf

# Figure 6
# performance evolution budgets  
python exploration_plotting/exploration_plotting.py -p performance_evolution_budget  -i /Users/jo/development/rise-lang/shine/experiments/exploration/results -n budget_pe -f pdf

# # stats
python exploration_plotting/exploration_plotting.py -p stats -i /Users/jo/development/rise-lang/shine/experiments/exploration/results/acoustic -n acoustic --log -f pdf 
python exploration_plotting/exploration_plotting.py -p stats -i /Users/jo/development/rise-lang/shine/experiments/exploration/results/asum -n asum  --log -f pdf 
python exploration_plotting/exploration_plotting.py -p stats -i /Users/jo/development/rise-lang/shine/experiments/exploration/results/kmeans -n kmeans --log -f pdf 
python exploration_plotting/exploration_plotting.py -p stats -i /Users/jo/development/rise-lang/shine/experiments/exploration/results/mm -n mm  --log -f pdf 
python exploration_plotting/exploration_plotting.py -p stats -i /Users/jo/development/rise-lang/shine/experiments/exploration/results/scal -n scal  --log -f pdf 


# RQ3: How does the performance stack up/how much performance is contributed by rewriting and paramter auto-tuning? 
# # Figure 7
python exploration_plotting/exploration_plotting.py -p speedup_stack  -i /Users/jo/development/rise-lang/shine/experiments/exploration/results -n speedup_stack -f pdf --plot_invalid