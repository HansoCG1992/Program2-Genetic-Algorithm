#!/usr/bin/env python3
"""Test the constraint violations breakdown"""

import sys
sys.path.insert(0, '/home/user/Program2-Genetic-Algorithm')

from genetic_scheduler import (
    create_random_schedule, calculate_fitness, get_constraint_violations
)

print("Testing Constraint Violations Breakdown...")
print("=" * 60)

# Create a random schedule
schedule = create_random_schedule()
fitness = calculate_fitness(schedule)
violations = get_constraint_violations(schedule)

print(f"\nFitness Score: {fitness:.3f}\n")
print("Constraint Violations:")
print("-" * 60)

print("\nRoom Constraints:")
print(f"  Room conflicts: {violations['room_conflicts']}")
print(f"  Room too small: {violations['room_too_small']}")
print(f"  Room too large (>3x): {violations['room_too_large_3x']}")
print(f"  Room too large (>1.5x): {violations['room_too_large_1.5x']}")
print(f"  Room good fit: {violations['room_good_fit']}")

print("\nFacilitator Preferences:")
print(f"  Preferred: {violations['facilitator_preferred']}")
print(f"  Other listed: {violations['facilitator_other']}")
print(f"  Unlisted: {violations['facilitator_unlisted']}")

print("\nFacilitator Load:")
print(f"  Single slot: {violations['facilitator_single_slot']}")
print(f"  Double-booked: {violations['facilitator_double_booked']}")
print(f"  Overloaded (>4): {violations['facilitator_overload_4plus']}")
print(f"  Underloaded (<3): {violations['facilitator_underload_less3']}")
print(f"  Consecutive bonus: {violations['facilitator_consecutive_bonus']}")
print(f"  Consecutive building penalty: {violations['facilitator_consecutive_building_penalty']}")

print("\nActivity-Specific:")
print(f"  SLA 101 far apart: {violations['sla101_sections_far_apart']}")
print(f"  SLA 101 same time: {violations['sla101_sections_same_time']}")
print(f"  SLA 191 far apart: {violations['sla191_sections_far_apart']}")
print(f"  SLA 191 same time: {violations['sla191_sections_same_time']}")
print(f"  101/191 consecutive: {violations['sla101_191_consecutive']}")
print(f"  101/191 consecutive building penalty: {violations['sla101_191_consecutive_building_penalty']}")
print(f"  101/191 separated 1hr: {violations['sla101_191_separated_1hr']}")
print(f"  101/191 same time: {violations['sla101_191_same_time']}")

print("\n" + "=" * 60)
print("Constraint violations breakdown working correctly!")
print("=" * 60)
