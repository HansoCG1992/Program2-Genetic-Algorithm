## SANITY CHECK: Requirements vs Implementation

### ✅ CORRECTLY IMPLEMENTED (verified line numbers)

1. **Activity Data Matches Appendix A** (lines 43-55)
   - All 11 activities with correct enrollments ✓
   - Preferred facilitators correctly listed ✓
   - Other facilitators correctly listed ✓
   - Example: SLA101A has enrollment 40, preferred [Glen, Lock, Banks], other [Numen, Richards, Shaw, Singer]

2. **Room Data Matches Appendix A** (lines 58-68)
   - All 9 rooms with correct capacities ✓
   - Beach 201 (18), Beach 301 (25), Frank 119 (95), Loft 206 (55), Loft 310 (48), James 325 (110), Roman 201 (40), Roman 216 (80), Slater 003 (32)

3. **Room Conflict Checking** (lines 137-139)
   - Detects when 2+ activities scheduled in same room at same time: -0.5 ✓

4. **Facilitator Conflict Checking** (lines 160-163)
   - Only 1 activity in time slot: +0.2 ✓
   - Multiple activities in time slot: -0.2 ✓

5. **Room Size Constraints** (lines 141-149)
   - Too small (enrollment > capacity): -0.5 ✓
   - Too large (> 3x enrollment): -0.4 ✓
   - Large (> 1.5x enrollment): -0.2 ✓
   - Good fit: +0.3 ✓

6. **Facilitator Preferences** (lines 151-157)
   - Handles MULTIPLE preferred facilitators using `in` operator ✓
   - Preferred: +0.5 ✓
   - Other: +0.2 ✓
   - Unlisted: -0.1 ✓

7. **Facilitator Load** (lines 165-172)
   - More than 4 total: -0.5 ✓
   - Less than 3 total: -0.4 (except Tyler < 2) ✓

8. **SLA 101/191 Spacing Rules** (lines 198-238)
   - Sections > 4 hours apart: +0.5 ✓
   - Sections at same time: -0.5 ✓
   - 101 and 191 consecutive: +0.5 ✓
   - Consecutive but different buildings (Roman/Beach): -0.4 ✓
   - Separated by 1 hour: +0.25 ✓
   - Same time: -0.25 ✓

9. **Tournament Selection** (lines 273-277)
   - Proper tournament selection with size=5 ✓
   - NOT just "sorted(pop)[0:10]" ✓

10. **Mutation with Probability** (lines 251-270)
    - Uses mutation_rate probability ✓
    - Random gene selection (room/time/facilitator) ✓

11. **Chromosome Validity**
    - Each activity appears exactly once (by design of assignments[i] = activity i) ✓
    - No duplicates possible ✓

---

### ✅ ISSUES FIXED (as of latest commit)

**1. FIXED: Facilitator Consecutive Time Slots** (lines 174-206)
   - Now properly applies +0.5 bonus for consecutive slots
   - Checks building separation (Roman/Beach) and applies -0.4 penalty
   - Fully implements: "Same rules as for SLA 191 and SLA 101"

**2. FIXED: SLA449 Data** (line 53)
   - Updated to match Appendix A exactly: ["Zeldin", "Shaw"] in other_facilitators
   - Now matches literal specification

**3. ADDED: Constraint Violations Breakdown**
   - New function get_constraint_violations() provides detailed counts
   - Output file shows complete breakdown of all constraint types
   - Console shows summary of key violations
   - Helps identify specific problems in generated schedules

---

### 🎁 OPTIONAL FEATURES NOT IMPLEMENTED (from assignment "OPTIONAL interesting constraints")

These were marked OPTIONAL - do you want them?

1. **Equipment Requirements**
   - SLA304, SLA303, SLA191, SLA291, SLA449, SLA451 require specific equipment
   - Rooms have different equipment (Labs, Projectors)
   - Scoring: both met +0.2, one met -0.1, none met -0.3

2. **Time Slot Preferences**
   - Glen prefers morning (10 AM, 11 AM): +0.1
   - Tyler prefers afternoon (2 PM, 3 PM): +0.1
   - Singer avoids noon: -0.3
   - Etc.

3. **Enhanced Output**
   - Penalty breakdown by category
   - Constraint violation counts
   - Room utilization pie chart
   - Course load bar chart

4. **Advanced Features**
   - Log file with timestamped best schedules
   - Automatic mutation rate tracker
   - GUI (worth +5 bonus points!)

---

### 🔧 RECOMMENDED FIXES

**Priority 1: Fix the consecutive facilitator time slots rule**
**Priority 2: Clarify SLA449 data**
**Priority 3: Ask if you want optional equipment requirements**

