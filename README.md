# Program2-Genetic-Algorithm

A Genetic Algorithm scheduler for a made up Seminar Association course scheduling problem.

## Overview

This program uses a genetic algorithm to optimize course schedules by balancing multiple constraints including:
- Room capacity and availability
- Facilitator preferences and workload
- Time slot conflicts
- Activity-specific rules (e.g., SLA 101/191 spacing requirements)

## Features

- **Mutation Operation**: Implements configurable mutation with adaptive rate adjustment
- **Adaptive Mutation Rate**: Automatically reduces mutation rate when improvement slows
- **Tournament Selection**: Uses tournament selection for parent selection
- **Elitism**: Preserves top 10% of population between generations
- **Performance Tracking**: Tracks best, average, and worst fitness across generations
- **Comprehensive Fitness Function**: Implements all specified constraints and penalties
- **Output Generation**: Creates schedule files and fitness charts

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python genetic_scheduler.py
```

## Output

The program generates:
1. `best_schedule.txt` - The optimized schedule sorted by time slot
2. `fitness_history.csv` - Complete fitness data for all generations
3. Console output with fitness chart (requires plotext)

## Algorithm Details

### Genetic Operations

- **Selection**: Tournament selection (size=5)
- **Crossover**: Single-point crossover
- **Mutation**: Random gene mutation with adaptive rate
  - Initial rate: 0.01 (1%)
  - Automatically halved when improvement < 2%
  - Minimum rate: 0.0001

### Termination Conditions

- Minimum 100 generations
- Stops when average fitness improvement < 1%
- Maximum 1000 generations (safety limit)

### Population

- Size: 500 individuals
- Random initialization
- Elitism: Top 10% preserved each generation

## Fitness Function

The fitness function evaluates schedules based on:

1. **Room Conflicts**: -0.5 for double-booking
2. **Room Size**: Penalties for mismatched capacity
3. **Facilitator Preferences**: +0.5 for preferred, +0.2 for listed, -0.1 for unlisted
4. **Facilitator Load**: Penalties for overload and underload
5. **Activity-Specific Rules**: Special constraints for SLA 101/191 sections

See `genetic_scheduler.py` for complete fitness function implementation.

## Data

- **11 Activities**: SLA101A, SLA101B, SLA191A, SLA191B, SLA201, SLA291, SLA303, SLA304, SLA394, SLA449, SLA451
- **9 Rooms**: Beach 201/301, Frank 119, Loft 206/310, James 325, Roman 201/216, Slater 003
- **6 Time Slots**: 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM
- **10 Facilitators**: Lock, Glen, Banks, Richards, Shaw, Singer, Uther, Tyler, Numen, Zeldin

## Performance

Typical runtime: 1-5 minutes (depending on convergence)
Expected best fitness: 10-15+ (varies based on random initialization)

## Author

Genetic Algorithm implementation for course scheduling optimization.
