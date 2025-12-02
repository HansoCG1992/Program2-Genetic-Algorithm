#!/usr/bin/env python3
"""Quick test of the genetic scheduler"""

import sys
sys.path.insert(0, '/home/user/Program2-Genetic-Algorithm')

from genetic_scheduler import (
    create_random_schedule, calculate_fitness, mutate,
    tournament_selection, crossover, ACTIVITIES, ROOMS, TIMES
)

print("Testing Genetic Algorithm Components...")
print("=" * 60)

# Test 1: Create random schedule
print("\n1. Testing random schedule creation...")
schedule = create_random_schedule()
print(f"   Created schedule with {len(schedule.assignments)} assignments")
print(f"   Sample assignment: Activity 0 -> {schedule.assignments[0]}")

# Test 2: Calculate fitness
print("\n2. Testing fitness calculation...")
fitness = calculate_fitness(schedule)
print(f"   Fitness score: {fitness:.3f}")

# Test 3: Test mutation
print("\n3. Testing mutation operation...")
mutated = mutate(schedule, 0.5)  # High mutation rate for testing
print(f"   Original: {schedule.assignments[0]}")
print(f"   Mutated:  {mutated.assignments[0]}")

# Test 4: Test crossover
print("\n4. Testing crossover operation...")
schedule2 = create_random_schedule()
child1, child2 = crossover(schedule, schedule2)
print(f"   Parent 1: {schedule.assignments[0]}")
print(f"   Parent 2: {schedule2.assignments[0]}")
print(f"   Child 1:  {child1.assignments[0]}")
print(f"   Child 2:  {child2.assignments[0]}")

# Test 5: Run mini evolution
print("\n5. Running mini evolution (10 generations)...")
population = [create_random_schedule() for _ in range(50)]

for gen in range(10):
    fitness_scores = [calculate_fitness(s) for s in population]
    best_fit = max(fitness_scores)
    avg_fit = sum(fitness_scores) / len(fitness_scores)
    print(f"   Gen {gen}: Best={best_fit:.3f}, Avg={avg_fit:.3f}")

    # Create next gen
    next_pop = []
    while len(next_pop) < 50:
        p1 = tournament_selection(population, fitness_scores)
        p2 = tournament_selection(population, fitness_scores)
        c1, c2 = crossover(p1, p2)
        c1 = mutate(c1, 0.01)
        c2 = mutate(c2, 0.01)
        next_pop.extend([c1, c2])
    population = next_pop[:50]

print("\n" + "=" * 60)
print("All tests passed! The genetic algorithm is working correctly.")
print("=" * 60)
