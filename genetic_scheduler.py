#!/usr/bin/env python3
"""
Genetic Algorithm for Course Scheduling
Implements a GA to optimize course schedules based on multiple constraints
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict
import random
from datetime import datetime

# Use cryptographically stronger random generator as suggested
rng = np.random.Generator(np.random.PCG64())


@dataclass
class Activity:
    """Represents a course activity"""
    name: str
    enrollment: int
    preferred_facilitators: List[str]
    other_facilitators: List[str]


@dataclass
class Room:
    """Represents a classroom"""
    name: str
    capacity: int


@dataclass
class Schedule:
    """Represents a complete schedule (chromosome)"""
    assignments: List[Tuple[int, int, int]]  # [(activity_idx, room_idx, time_idx, facilitator_idx)]

    def __init__(self, num_activities: int):
        self.assignments = [(0, 0, 0, 0) for _ in range(num_activities)]


# Constants - Activities
ACTIVITIES = [
    Activity("SLA101A", 40, ["Glen", "Lock", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]),
    Activity("SLA101B", 35, ["Glen", "Lock", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]),
    Activity("SLA191A", 45, ["Glen", "Lock", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]),
    Activity("SLA191B", 40, ["Glen", "Lock", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]),
    Activity("SLA201", 60, ["Glen", "Banks", "Zeldin", "Lock", "Singer"], ["Richards", "Uther", "Shaw"]),
    Activity("SLA291", 50, ["Glen", "Banks", "Zeldin", "Lock", "Singer"], ["Richards", "Uther", "Shaw"]),
    Activity("SLA303", 25, ["Glen", "Zeldin"], ["Banks"]),
    Activity("SLA304", 20, ["Singer", "Uther"], ["Richards"]),
    Activity("SLA394", 15, ["Tyler", "Singer"], ["Richards", "Zeldin"]),
    Activity("SLA449", 30, ["Tyler", "Zeldin", "Uther"], ["Zeldin", "Shaw"]),
    Activity("SLA451", 90, ["Lock", "Banks", "Zeldin"], ["Tyler", "Singer", "Shaw", "Glen"])
]

# Constants - Rooms
ROOMS = [
    Room("Beach 201", 18),
    Room("Beach 301", 25),
    Room("Frank 119", 95),
    Room("Loft 206", 55),
    Room("Loft 310", 48),
    Room("James 325", 110),
    Room("Roman 201", 40),
    Room("Roman 216", 80),
    Room("Slater 003", 32)
]

# Constants - Time slots
TIMES = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]

# Constants - Facilitators
FACILITATORS = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]

# Genetic Algorithm Parameters
POPULATION_SIZE = 500
INITIAL_MUTATION_RATE = 0.01
MIN_GENERATIONS = 100
IMPROVEMENT_THRESHOLD = 0.01  # 1% improvement threshold
TOURNAMENT_SIZE = 5


def create_random_schedule() -> Schedule:
    """Creates a random schedule (chromosome)"""
    schedule = Schedule(len(ACTIVITIES))
    for i in range(len(ACTIVITIES)):
        room_idx = int(rng.integers(0, len(ROOMS)))
        time_idx = int(rng.integers(0, len(TIMES)))
        facilitator_idx = int(rng.integers(0, len(FACILITATORS)))
        schedule.assignments[i] = (i, room_idx, time_idx, facilitator_idx)
    return schedule


def calculate_fitness(schedule: Schedule) -> float:
    """
    Calculates fitness score for a schedule based on all constraints.
    Higher score is better.
    """
    fitness = 0.0

    # Create lookup structures for efficient checking
    time_room_activities = {}  # (time_idx, room_idx) -> [activity_indices]
    time_facilitator_activities = {}  # (time_idx, facilitator_idx) -> [activity_indices]
    facilitator_total_activities = {}  # facilitator_idx -> count
    facilitator_time_slots = {}  # facilitator_idx -> [time_indices]

    # Build lookup structures
    for activity_idx, (_, room_idx, time_idx, facilitator_idx) in enumerate(schedule.assignments):
        # Track room usage
        key = (time_idx, room_idx)
        if key not in time_room_activities:
            time_room_activities[key] = []
        time_room_activities[key].append(activity_idx)

        # Track facilitator usage
        key = (time_idx, facilitator_idx)
        if key not in time_facilitator_activities:
            time_facilitator_activities[key] = []
        time_facilitator_activities[key].append(activity_idx)

        # Track total activities per facilitator
        facilitator_total_activities[facilitator_idx] = facilitator_total_activities.get(facilitator_idx, 0) + 1

        # Track time slots per facilitator
        if facilitator_idx not in facilitator_time_slots:
            facilitator_time_slots[facilitator_idx] = []
        if time_idx not in facilitator_time_slots[facilitator_idx]:
            facilitator_time_slots[facilitator_idx].append(time_idx)

    # Evaluate each activity
    for activity_idx, (_, room_idx, time_idx, facilitator_idx) in enumerate(schedule.assignments):
        activity = ACTIVITIES[activity_idx]
        room = ROOMS[room_idx]
        facilitator = FACILITATORS[facilitator_idx]

        # Check for room conflicts (same time, same room)
        if len(time_room_activities[(time_idx, room_idx)]) > 1:
            fitness -= 0.5

        # Room size evaluation
        if activity.enrollment > room.capacity:
            fitness -= 0.5
        elif room.capacity > 3 * activity.enrollment:
            fitness -= 0.4
        elif room.capacity > 1.5 * activity.enrollment:
            fitness -= 0.2
        else:
            fitness += 0.3

        # Facilitator preference
        if facilitator in activity.preferred_facilitators:
            fitness += 0.5
        elif facilitator in activity.other_facilitators:
            fitness += 0.2
        else:
            fitness -= 0.1

        # Facilitator load - scheduled for only 1 activity in this time slot
        if len(time_facilitator_activities[(time_idx, facilitator_idx)]) == 1:
            fitness += 0.2
        elif len(time_facilitator_activities[(time_idx, facilitator_idx)]) > 1:
            fitness -= 0.2

        # Facilitator total load
        total_load = facilitator_total_activities[facilitator_idx]
        if total_load > 4:
            fitness -= 0.5
        elif total_load < 3:
            # Exception for Dr. Tyler
            if facilitator != "Tyler" or total_load >= 2:
                fitness -= 0.4

    # Check for consecutive time slots for facilitators
    for facilitator_idx, time_slots in facilitator_time_slots.items():
        sorted_times = sorted(time_slots)
        for i in range(len(sorted_times) - 1):
            if sorted_times[i+1] - sorted_times[i] == 1:
                # Facilitator has consecutive time slots - apply SLA 191/101 rules
                time1 = sorted_times[i]
                time2 = sorted_times[i+1]

                # Find activities at these times for this facilitator
                activities_at_time1 = [act_idx for act_idx, (_, r, t, f) in enumerate(schedule.assignments)
                                      if t == time1 and f == facilitator_idx]
                activities_at_time2 = [act_idx for act_idx, (_, r, t, f) in enumerate(schedule.assignments)
                                      if t == time2 and f == facilitator_idx]

                # Apply bonus for consecutive slots
                fitness += 0.5

                # Check building separation penalty
                for act1_idx in activities_at_time1:
                    for act2_idx in activities_at_time2:
                        room1_idx = schedule.assignments[act1_idx][1]
                        room2_idx = schedule.assignments[act2_idx][1]

                        room1_name = ROOMS[room1_idx].name
                        room2_name = ROOMS[room2_idx].name

                        room1_in_roman_beach = room1_name.startswith("Roman") or room1_name.startswith("Beach")
                        room2_in_roman_beach = room2_name.startswith("Roman") or room2_name.startswith("Beach")

                        # If one is in Roman/Beach and other isn't, penalize
                        if room1_in_roman_beach != room2_in_roman_beach:
                            fitness -= 0.4

    # Activity-specific constraints
    sla101a_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA101A")
    sla101b_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA101B")
    sla191a_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA191A")
    sla191b_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA191B")

    time_101a = schedule.assignments[sla101a_idx][2]
    time_101b = schedule.assignments[sla101b_idx][2]
    time_191a = schedule.assignments[sla191a_idx][2]
    time_191b = schedule.assignments[sla191b_idx][2]

    room_101a = schedule.assignments[sla101a_idx][1]
    room_101b = schedule.assignments[sla101b_idx][1]
    room_191a = schedule.assignments[sla191a_idx][1]
    room_191b = schedule.assignments[sla191b_idx][1]

    # SLA 101 sections more than 4 hours apart
    if abs(time_101a - time_101b) > 4:
        fitness += 0.5
    # SLA 101 sections at same time
    if time_101a == time_101b:
        fitness -= 0.5

    # SLA 191 sections more than 4 hours apart
    if abs(time_191a - time_191b) > 4:
        fitness += 0.5
    # SLA 191 sections at same time
    if time_191a == time_191b:
        fitness -= 0.5

    # Check all combinations of SLA 191 and SLA 101 sections
    for sla191_idx, sla191_time, sla191_room in [(sla191a_idx, time_191a, room_191a),
                                                    (sla191b_idx, time_191b, room_191b)]:
        for sla101_idx, sla101_time, sla101_room in [(sla101a_idx, time_101a, room_101a),
                                                       (sla101b_idx, time_101b, room_101b)]:
            time_diff = abs(sla191_time - sla101_time)

            # Consecutive time slots
            if time_diff == 1:
                fitness += 0.5
                # Check if one is in Roman/Beach and other isn't
                sla191_room_name = ROOMS[sla191_room].name
                sla101_room_name = ROOMS[sla101_room].name

                sla191_in_roman_beach = sla191_room_name.startswith("Roman") or sla191_room_name.startswith("Beach")
                sla101_in_roman_beach = sla101_room_name.startswith("Roman") or sla101_room_name.startswith("Beach")

                if sla191_in_roman_beach != sla101_in_roman_beach:
                    fitness -= 0.4

            # Separated by 1 hour (e.g., 10 AM and 12 PM)
            elif time_diff == 2:
                fitness += 0.25

            # Same time slot
            elif time_diff == 0:
                fitness -= 0.25

    return fitness


def get_constraint_violations(schedule: Schedule) -> Dict[str, int]:
    """
    Returns a dictionary of constraint violation counts for detailed reporting.
    """
    violations = {
        "room_conflicts": 0,
        "room_too_small": 0,
        "room_too_large_1.5x": 0,
        "room_too_large_3x": 0,
        "room_good_fit": 0,
        "facilitator_preferred": 0,
        "facilitator_other": 0,
        "facilitator_unlisted": 0,
        "facilitator_single_slot": 0,
        "facilitator_double_booked": 0,
        "facilitator_overload_4plus": 0,
        "facilitator_underload_less3": 0,
        "facilitator_consecutive_bonus": 0,
        "facilitator_consecutive_building_penalty": 0,
        "sla101_sections_far_apart": 0,
        "sla101_sections_same_time": 0,
        "sla191_sections_far_apart": 0,
        "sla191_sections_same_time": 0,
        "sla101_191_consecutive": 0,
        "sla101_191_consecutive_building_penalty": 0,
        "sla101_191_separated_1hr": 0,
        "sla101_191_same_time": 0
    }

    # Create lookup structures
    time_room_activities = {}
    time_facilitator_activities = {}
    facilitator_total_activities = {}
    facilitator_time_slots = {}

    for activity_idx, (_, room_idx, time_idx, facilitator_idx) in enumerate(schedule.assignments):
        key = (time_idx, room_idx)
        if key not in time_room_activities:
            time_room_activities[key] = []
        time_room_activities[key].append(activity_idx)

        key = (time_idx, facilitator_idx)
        if key not in time_facilitator_activities:
            time_facilitator_activities[key] = []
        time_facilitator_activities[key].append(activity_idx)

        facilitator_total_activities[facilitator_idx] = facilitator_total_activities.get(facilitator_idx, 0) + 1

        if facilitator_idx not in facilitator_time_slots:
            facilitator_time_slots[facilitator_idx] = []
        if time_idx not in facilitator_time_slots[facilitator_idx]:
            facilitator_time_slots[facilitator_idx].append(time_idx)

    # Count violations per activity
    for activity_idx, (_, room_idx, time_idx, facilitator_idx) in enumerate(schedule.assignments):
        activity = ACTIVITIES[activity_idx]
        room = ROOMS[room_idx]
        facilitator = FACILITATORS[facilitator_idx]

        # Room conflicts
        if len(time_room_activities[(time_idx, room_idx)]) > 1:
            violations["room_conflicts"] += 1

        # Room size
        if activity.enrollment > room.capacity:
            violations["room_too_small"] += 1
        elif room.capacity > 3 * activity.enrollment:
            violations["room_too_large_3x"] += 1
        elif room.capacity > 1.5 * activity.enrollment:
            violations["room_too_large_1.5x"] += 1
        else:
            violations["room_good_fit"] += 1

        # Facilitator preference
        if facilitator in activity.preferred_facilitators:
            violations["facilitator_preferred"] += 1
        elif facilitator in activity.other_facilitators:
            violations["facilitator_other"] += 1
        else:
            violations["facilitator_unlisted"] += 1

        # Facilitator load per time slot
        if len(time_facilitator_activities[(time_idx, facilitator_idx)]) == 1:
            violations["facilitator_single_slot"] += 1
        elif len(time_facilitator_activities[(time_idx, facilitator_idx)]) > 1:
            violations["facilitator_double_booked"] += 1

        # Facilitator total load
        total_load = facilitator_total_activities[facilitator_idx]
        if total_load > 4:
            violations["facilitator_overload_4plus"] += 1
        elif total_load < 3:
            if facilitator != "Tyler" or total_load >= 2:
                violations["facilitator_underload_less3"] += 1

    # Check consecutive facilitator time slots
    for facilitator_idx, time_slots in facilitator_time_slots.items():
        sorted_times = sorted(time_slots)
        for i in range(len(sorted_times) - 1):
            if sorted_times[i+1] - sorted_times[i] == 1:
                violations["facilitator_consecutive_bonus"] += 1

                time1 = sorted_times[i]
                time2 = sorted_times[i+1]

                activities_at_time1 = [act_idx for act_idx, (_, r, t, f) in enumerate(schedule.assignments)
                                      if t == time1 and f == facilitator_idx]
                activities_at_time2 = [act_idx for act_idx, (_, r, t, f) in enumerate(schedule.assignments)
                                      if t == time2 and f == facilitator_idx]

                for act1_idx in activities_at_time1:
                    for act2_idx in activities_at_time2:
                        room1_idx = schedule.assignments[act1_idx][1]
                        room2_idx = schedule.assignments[act2_idx][1]
                        room1_name = ROOMS[room1_idx].name
                        room2_name = ROOMS[room2_idx].name
                        room1_in_roman_beach = room1_name.startswith("Roman") or room1_name.startswith("Beach")
                        room2_in_roman_beach = room2_name.startswith("Roman") or room2_name.startswith("Beach")
                        if room1_in_roman_beach != room2_in_roman_beach:
                            violations["facilitator_consecutive_building_penalty"] += 1

    # Activity-specific constraints
    sla101a_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA101A")
    sla101b_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA101B")
    sla191a_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA191A")
    sla191b_idx = next(i for i, a in enumerate(ACTIVITIES) if a.name == "SLA191B")

    time_101a = schedule.assignments[sla101a_idx][2]
    time_101b = schedule.assignments[sla101b_idx][2]
    time_191a = schedule.assignments[sla191a_idx][2]
    time_191b = schedule.assignments[sla191b_idx][2]

    room_101a = schedule.assignments[sla101a_idx][1]
    room_101b = schedule.assignments[sla101b_idx][1]
    room_191a = schedule.assignments[sla191a_idx][1]
    room_191b = schedule.assignments[sla191b_idx][1]

    # SLA 101 sections spacing
    if abs(time_101a - time_101b) > 4:
        violations["sla101_sections_far_apart"] += 1
    if time_101a == time_101b:
        violations["sla101_sections_same_time"] += 1

    # SLA 191 sections spacing
    if abs(time_191a - time_191b) > 4:
        violations["sla191_sections_far_apart"] += 1
    if time_191a == time_191b:
        violations["sla191_sections_same_time"] += 1

    # SLA 101 and 191 interactions
    for sla191_idx, sla191_time, sla191_room in [(sla191a_idx, time_191a, room_191a),
                                                    (sla191b_idx, time_191b, room_191b)]:
        for sla101_idx, sla101_time, sla101_room in [(sla101a_idx, time_101a, room_101a),
                                                       (sla101b_idx, time_101b, room_101b)]:
            time_diff = abs(sla191_time - sla101_time)

            if time_diff == 1:
                violations["sla101_191_consecutive"] += 1
                sla191_room_name = ROOMS[sla191_room].name
                sla101_room_name = ROOMS[sla101_room].name
                sla191_in_roman_beach = sla191_room_name.startswith("Roman") or sla191_room_name.startswith("Beach")
                sla101_in_roman_beach = sla101_room_name.startswith("Roman") or sla101_room_name.startswith("Beach")
                if sla191_in_roman_beach != sla101_in_roman_beach:
                    violations["sla101_191_consecutive_building_penalty"] += 1
            elif time_diff == 2:
                violations["sla101_191_separated_1hr"] += 1
            elif time_diff == 0:
                violations["sla101_191_same_time"] += 1

    return violations


def mutate(schedule: Schedule, mutation_rate: float) -> Schedule:
    """
    Applies mutation to a schedule.
    For each gene, with probability mutation_rate, randomly changes it.
    """
    mutated = Schedule(len(ACTIVITIES))
    mutated.assignments = list(schedule.assignments)

    for i in range(len(mutated.assignments)):
        if rng.random() < mutation_rate:
            # Randomly select what to mutate: room, time, or facilitator
            mutation_type = int(rng.integers(0, 3))

            activity_idx, room_idx, time_idx, facilitator_idx = mutated.assignments[i]

            if mutation_type == 0:
                # Mutate room
                room_idx = int(rng.integers(0, len(ROOMS)))
            elif mutation_type == 1:
                # Mutate time
                time_idx = int(rng.integers(0, len(TIMES)))
            else:
                # Mutate facilitator
                facilitator_idx = int(rng.integers(0, len(FACILITATORS)))

            mutated.assignments[i] = (activity_idx, room_idx, time_idx, facilitator_idx)

    return mutated


def tournament_selection(population: List[Schedule], fitness_scores: List[float]) -> Schedule:
    """Selects a schedule using tournament selection"""
    tournament_indices = rng.choice(len(population), size=TOURNAMENT_SIZE, replace=False)
    best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
    return population[best_idx]


def crossover(parent1: Schedule, parent2: Schedule) -> Tuple[Schedule, Schedule]:
    """
    Performs single-point crossover between two parent schedules.
    Returns two offspring.
    """
    crossover_point = int(rng.integers(1, len(ACTIVITIES)))

    child1 = Schedule(len(ACTIVITIES))
    child2 = Schedule(len(ACTIVITIES))

    child1.assignments = parent1.assignments[:crossover_point] + parent2.assignments[crossover_point:]
    child2.assignments = parent2.assignments[:crossover_point] + parent1.assignments[crossover_point:]

    return child1, child2


def print_schedule(schedule: Schedule, filename: str = "best_schedule.txt"):
    """Prints the schedule to a file with constraint violations breakdown"""
    fitness = calculate_fitness(schedule)
    violations = get_constraint_violations(schedule)

    with open(filename, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("OPTIMIZED COURSE SCHEDULE\n")
        f.write("=" * 80 + "\n")
        f.write(f"Overall Fitness Score: {fitness:.4f}\n")
        f.write("=" * 80 + "\n\n")

        # Print constraint violations breakdown
        f.write("CONSTRAINT VIOLATIONS BREAKDOWN\n")
        f.write("-" * 80 + "\n")

        f.write("\nRoom Constraints:\n")
        f.write(f"  Room conflicts (double-booked): {violations['room_conflicts']}\n")
        f.write(f"  Room too small: {violations['room_too_small']}\n")
        f.write(f"  Room too large (>3x): {violations['room_too_large_3x']}\n")
        f.write(f"  Room too large (>1.5x): {violations['room_too_large_1.5x']}\n")
        f.write(f"  Room good fit: {violations['room_good_fit']}\n")

        f.write("\nFacilitator Preferences:\n")
        f.write(f"  Preferred facilitator: {violations['facilitator_preferred']}\n")
        f.write(f"  Other listed facilitator: {violations['facilitator_other']}\n")
        f.write(f"  Unlisted facilitator: {violations['facilitator_unlisted']}\n")

        f.write("\nFacilitator Load:\n")
        f.write(f"  Single activity in time slot: {violations['facilitator_single_slot']}\n")
        f.write(f"  Double-booked in time slot: {violations['facilitator_double_booked']}\n")
        f.write(f"  Overloaded (>4 activities): {violations['facilitator_overload_4plus']}\n")
        f.write(f"  Underloaded (<3 activities): {violations['facilitator_underload_less3']}\n")
        f.write(f"  Consecutive time slots (bonus): {violations['facilitator_consecutive_bonus']}\n")
        f.write(f"  Consecutive different buildings (penalty): {violations['facilitator_consecutive_building_penalty']}\n")

        f.write("\nActivity-Specific Constraints:\n")
        f.write(f"  SLA 101 sections >4 hrs apart (bonus): {violations['sla101_sections_far_apart']}\n")
        f.write(f"  SLA 101 sections same time (penalty): {violations['sla101_sections_same_time']}\n")
        f.write(f"  SLA 191 sections >4 hrs apart (bonus): {violations['sla191_sections_far_apart']}\n")
        f.write(f"  SLA 191 sections same time (penalty): {violations['sla191_sections_same_time']}\n")
        f.write(f"  SLA 101/191 consecutive (bonus): {violations['sla101_191_consecutive']}\n")
        f.write(f"  SLA 101/191 consecutive diff buildings (penalty): {violations['sla101_191_consecutive_building_penalty']}\n")
        f.write(f"  SLA 101/191 separated by 1 hr (bonus): {violations['sla101_191_separated_1hr']}\n")
        f.write(f"  SLA 101/191 same time (penalty): {violations['sla101_191_same_time']}\n")

        f.write("\n" + "=" * 80 + "\n\n")

        # Print schedule sorted by time
        f.write("SCHEDULE BY TIME SLOT\n")
        f.write("=" * 80 + "\n")

        sorted_assignments = sorted(enumerate(schedule.assignments),
                                   key=lambda x: (x[1][2], x[1][1]))

        current_time = -1
        for activity_idx, (_, room_idx, time_idx, facilitator_idx) in sorted_assignments:
            if time_idx != current_time:
                current_time = time_idx
                f.write(f"\n{TIMES[time_idx]}\n")
                f.write("-" * 80 + "\n")

            activity = ACTIVITIES[activity_idx]
            room = ROOMS[room_idx]
            facilitator = FACILITATORS[facilitator_idx]

            f.write(f"  {activity.name:12} | {room.name:15} | {facilitator:10} | ")
            f.write(f"Enrollment: {activity.enrollment:3} | Capacity: {room.capacity:3}\n")

        f.write("\n" + "=" * 80 + "\n")


def print_fitness_chart(generations: List[int], best_fitness: List[float],
                       avg_fitness: List[float], worst_fitness: List[float]):
    """Prints fitness chart using plotext"""
    try:
        import plotext as plt

        plt.clear_figure()
        plt.plot(generations, best_fitness, label="Best")
        plt.plot(generations, avg_fitness, label="Average")
        plt.plot(generations, worst_fitness, label="Worst")
        plt.title("Fitness over Generations")
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.show()
    except ImportError:
        print("\nNote: Install plotext for graphical output: pip install plotext")
        print("\nFitness data (first and last 10 generations):")
        print(f"{'Gen':>5} | {'Best':>10} | {'Average':>10} | {'Worst':>10}")
        print("-" * 50)

        # Show first 10
        for i in range(min(10, len(generations))):
            print(f"{generations[i]:5} | {best_fitness[i]:10.3f} | {avg_fitness[i]:10.3f} | {worst_fitness[i]:10.3f}")

        if len(generations) > 20:
            print("  ...")
            # Show last 10
            for i in range(max(10, len(generations) - 10), len(generations)):
                print(f"{generations[i]:5} | {best_fitness[i]:10.3f} | {avg_fitness[i]:10.3f} | {worst_fitness[i]:10.3f}")


def run_genetic_algorithm():
    """Main genetic algorithm loop"""
    print("=" * 80)
    print("GENETIC ALGORITHM COURSE SCHEDULER")
    print("=" * 80)
    print(f"\nPopulation Size: {POPULATION_SIZE}")
    print(f"Initial Mutation Rate: {INITIAL_MUTATION_RATE}")
    print(f"Minimum Generations: {MIN_GENERATIONS}")
    print(f"Activities: {len(ACTIVITIES)}, Rooms: {len(ROOMS)}, Times: {len(TIMES)}")
    print("\nStarting evolution...\n")

    # Initialize population
    population = [create_random_schedule() for _ in range(POPULATION_SIZE)]

    # Tracking variables
    generation = 0
    mutation_rate = INITIAL_MUTATION_RATE
    best_fitness_history = []
    avg_fitness_history = []
    worst_fitness_history = []
    generation_history = []

    previous_avg_fitness = float('-inf')

    while True:
        # Evaluate fitness
        fitness_scores = [calculate_fitness(schedule) for schedule in population]

        best_fitness = max(fitness_scores)
        avg_fitness = np.mean(fitness_scores)
        worst_fitness = min(fitness_scores)

        # Track metrics
        best_fitness_history.append(best_fitness)
        avg_fitness_history.append(avg_fitness)
        worst_fitness_history.append(worst_fitness)
        generation_history.append(generation)

        # Calculate improvement
        if generation > 0:
            improvement = ((avg_fitness - previous_avg_fitness) / abs(previous_avg_fitness)) * 100 if previous_avg_fitness != 0 else 0
        else:
            improvement = 0

        # Print progress every 10 generations
        if generation % 10 == 0:
            print(f"Gen {generation:4} | Best: {best_fitness:8.3f} | Avg: {avg_fitness:8.3f} | "
                  f"Worst: {worst_fitness:8.3f} | Improvement: {improvement:6.2f}% | "
                  f"Mutation Rate: {mutation_rate:.6f}")

        # Check termination conditions
        if generation >= MIN_GENERATIONS and improvement < IMPROVEMENT_THRESHOLD and improvement >= 0:
            print(f"\nConverged at generation {generation}")
            print(f"Final improvement: {improvement:.4f}%")
            break

        # Adaptive mutation rate adjustment (after sufficient generations)
        if generation > 50 and generation % 50 == 0:
            if improvement < 2.0 and mutation_rate > 0.0001:  # Slow improvement
                old_rate = mutation_rate
                mutation_rate /= 2
                print(f"\n  -> Mutation rate adjusted: {old_rate:.6f} -> {mutation_rate:.6f}")

        # Create next generation
        next_generation = []

        # Elitism: Keep best 10% of population
        elite_count = POPULATION_SIZE // 10
        elite_indices = np.argsort(fitness_scores)[-elite_count:]
        for idx in elite_indices:
            next_generation.append(population[idx])

        # Generate rest through selection, crossover, and mutation
        while len(next_generation) < POPULATION_SIZE:
            parent1 = tournament_selection(population, fitness_scores)
            parent2 = tournament_selection(population, fitness_scores)

            child1, child2 = crossover(parent1, parent2)

            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)

            next_generation.append(child1)
            if len(next_generation) < POPULATION_SIZE:
                next_generation.append(child2)

        population = next_generation
        previous_avg_fitness = avg_fitness
        generation += 1

        # Safety limit
        if generation >= 1000:
            print("\nReached maximum generation limit (1000)")
            break

    # Final results
    print("\n" + "=" * 80)
    print("EVOLUTION COMPLETE")
    print("=" * 80)

    final_fitness_scores = [calculate_fitness(schedule) for schedule in population]
    best_idx = np.argmax(final_fitness_scores)
    best_schedule = population[best_idx]
    best_fitness_final = final_fitness_scores[best_idx]

    print(f"\nFinal Generation: {generation}")
    print(f"Best Fitness: {best_fitness_final:.4f}")
    print(f"Average Fitness: {np.mean(final_fitness_scores):.4f}")
    print(f"Worst Fitness: {min(final_fitness_scores):.4f}")

    # Print constraint violations summary
    violations = get_constraint_violations(best_schedule)
    print("\n" + "-" * 80)
    print("CONSTRAINT VIOLATIONS SUMMARY (Best Schedule)")
    print("-" * 80)
    print(f"Room conflicts: {violations['room_conflicts']}")
    print(f"Room too small: {violations['room_too_small']}")
    print(f"Facilitator double-booked: {violations['facilitator_double_booked']}")
    print(f"Unlisted facilitators: {violations['facilitator_unlisted']}")
    print(f"Facilitator overloaded (>4): {violations['facilitator_overload_4plus']}")
    print(f"Facilitator underloaded (<3): {violations['facilitator_underload_less3']}")
    print("-" * 80)

    # Save best schedule
    print("\nSaving best schedule to 'best_schedule.txt'...")
    print_schedule(best_schedule)

    # Print fitness chart
    print("\n")
    print_fitness_chart(generation_history, best_fitness_history,
                       avg_fitness_history, worst_fitness_history)

    # Save fitness history to CSV
    with open("fitness_history.csv", 'w') as f:
        f.write("Generation,Best,Average,Worst\n")
        for i in range(len(generation_history)):
            f.write(f"{generation_history[i]},{best_fitness_history[i]},{avg_fitness_history[i]},{worst_fitness_history[i]}\n")
    print("\nFitness history saved to 'fitness_history.csv'")

    return best_schedule, best_fitness_final


if __name__ == "__main__":
    best_schedule, best_fitness = run_genetic_algorithm()
    print("\n" + "=" * 80)
    print("Program complete!")
    print("=" * 80)
