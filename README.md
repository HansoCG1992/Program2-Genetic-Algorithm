# Program 2 – Genetic Algorithm Scheduler
# Created by Cole Hanson

This project implements a genetic algorithm to generate an optimized schedule for a set of seminar activities.  
The goal is to place 11 courses into 9 rooms and 6 time slots while respecting all constraints from the assignment.

## Overview

The genetic algorithm evaluates each schedule using a fitness function that considers:

- room capacities  
- facilitator preferences  
- scheduling conflicts  
- facilitator workload  
- special spacing rules for SLA 101 and SLA 191 sections  

The program runs multiple generations and improves the population until it converges.

## How to Run

Install requirements:

```
pip install -r requirements.txt
```

Run the main program:

```
python genetic_scheduler.py
```

This generates:

- **best_schedule.txt** — final optimized schedule  
- **fitness_history.csv** — fitness data for each generation  
- Console output showing progress and a fitness graph (if `plotext` is installed)

## Main Features

- Tournament selection  
- Single-point crossover  
- Mutation with adaptive rate (rate cuts in half when improvement slows)  
- Elitism (top 10 percent carried forward)  
- Full assignment fitness rules implemented  
- Fitness chart (CLI)  
- Optional GUI (`gui.py`) for viewing the graph in a window  

## Optional GUI (Extra Credit)

A simple GUI is included (`gui.py`) that displays the final fitness graph in a window.  
Run it with:

```
python gui.py
```

This is optional and not required for grading.

## Data Used

- **11 activities** with enrollments and facilitator preferences  
- **9 rooms** with capacities  
- **6 time slots**  
- **10 facilitators**

All data matches the assignment handout.
