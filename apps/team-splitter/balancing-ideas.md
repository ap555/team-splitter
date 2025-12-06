## Rebalancing Design Ideas (Post Snake-Draft)

Keep the existing snake draft as-is, then apply rebalancing afterward.

---

### **Core Approach: Iterative Player Swaps**

After snake draft completes, try swapping players between teams to improve balance.

---

### **Swap Strategies**

#### **Strategy 1: Same-Role Swaps Only**
- Only swap players with the same role (D↔D, M↔M, S↔S)
- Preserves role distribution from snake draft
- Simpler logic, fewer combinations to try

#### **Strategy 2: Cross-Role Swaps**
- Allow swapping different roles (D↔M, M↔S, etc.)
- More flexibility to optimize
- Need to track role balance separately

**Recommendation:** Start with same-role swaps for simplicity and predictability.

---

### **Balance Scoring Function**

Create a scoring function that measures how "balanced" teams are:

```
balance_score = skill_variance + role_imbalance_penalty
```

**Skill Variance:**
- Standard deviation of team total skills
- Or: max skill difference between any two teams
- Lower is better

**Role Imbalance Penalty:**
- For each role, calculate difference in count across teams
- Sum all differences
- Lower is better

**Key:** No hard-coded thresholds - just minimize the score relative to current state.

---

### **Swap Evaluation**

For each potential swap:
1. Calculate current balance score
2. Simulate the swap (don't actually do it yet)
3. Calculate new balance score
4. If new score < current score: accept the swap
5. If new score ≥ current score: reject the swap

---

### **Swap Selection Algorithms**

#### **Option A: Greedy Best-First**
- Try all possible swap combinations
- Pick the swap that gives best improvement
- Apply it and repeat
- Stop when no swap improves score

**Pros:** Simple, deterministic
**Cons:** Can get stuck in local optimum

---

#### **Option B: Random Exploration with Acceptance Threshold**
- Randomly select swap pairs
- Accept swap if it improves score by any amount
- Use seeded random for determinism
- Run for fixed number of iterations

**Pros:** Faster than trying all combinations
**Cons:** Less optimal results

---

#### **Option C: Simulated Annealing (Sophisticated)**
- Start with high "temperature"
- Accept swaps that improve score
- Also accept bad swaps with probability based on temperature
- Gradually reduce temperature
- Helps escape local optima

**Pros:** Better global optimum
**Cons:** More complex, harder to tune

**Recommendation:** Start with **Greedy Best-First** - simpler and deterministic.

---

### **Iteration Limits**

Instead of hard-coded thresholds, use iteration-based stopping:

**Option A: Fixed Iterations**
- Try N rounds of swaps (e.g., 100 rounds)
- Each round: find best swap and apply it
- Stop after N rounds or when no improvement found

**Option B: Convergence-Based**
- Keep swapping until no improvement found for K consecutive rounds
- More adaptive to problem complexity

**Option C: Time-Based**
- Run for maximum T seconds
- Ensures performance bounds

**Recommendation:** **Convergence-based** - stops automatically when balanced.

---

### **Swap Pool Generation**

How to generate candidate swaps efficiently:

#### **Approach A: All Pairs**
- For each team pair (Team A, Team B)
- For each player in A and each player in B
- Try swapping them if same role
- Evaluate all combinations

**Pros:** Finds best swap
**Cons:** O(n²) combinations

---

#### **Approach B: Skill-Delta Targeting**
- Calculate skill difference between teams
- Only try swaps that would reduce the difference
- Example: If Team A > Team B, swap high-skill from A with low-skill from B

**Pros:** Much faster, smart filtering
**Cons:** Might miss non-obvious improvements

**Recommendation:** **Skill-Delta Targeting** for efficiency.

---

### **Implementation Design**

```python
def __rebalance_teams(self, teams: List[Team]) -> None:
    """Rebalance teams after initial draft by swapping players."""

    max_rounds_without_improvement = 10
    rounds_without_improvement = 0

    while rounds_without_improvement < max_rounds_without_improvement:
        current_score = self.__calculate_balance_score(teams)
        best_swap = self.__find_best_swap(teams, current_score)

        if best_swap is None:
            # No improving swap found
            rounds_without_improvement += 1
        else:
            # Apply the swap
            self.__apply_swap(teams, best_swap)
            rounds_without_improvement = 0
```

---

### **Balance Score Details**

```python
def __calculate_balance_score(self, teams: List[Team]) -> float:
    """Calculate how unbalanced the teams are. Lower is better."""

    # Skill balance component
    skills = [team.skill() for team in teams]
    skill_variance = statistics.stdev(skills) if len(skills) > 1 else 0

    # Role balance component (for each role)
    role_penalty = 0
    for role in Role:
        counts = [team.role_count(role) for team in teams]
        role_variance = max(counts) - min(counts)
        role_penalty += role_variance

    # Combined score (can weight components differently)
    return skill_variance + (role_penalty * weight_factor)
```

**Weight factor:** Could be adaptive based on total skill range vs role count range.

---

### **Adaptive Weighting**

Instead of hard-coded weights, make them proportional:

```python
# Normalize skill variance to 0-1 range
skill_range = max_skill - min_skill
normalized_skill_var = skill_variance / skill_range if skill_range > 0 else 0

# Normalize role penalty to 0-1 range
max_possible_role_imbalance = num_players  # worst case
normalized_role_penalty = role_penalty / max_possible_role_imbalance

# Combined score (both in similar range now)
return normalized_skill_var + normalized_role_penalty
```

---

### **Configuration Options**

Make rebalancing optional and configurable:

```python
def __init__(self, roster: List[Player], seed: Optional[int] = None,
             enable_rebalancing: bool = True) -> None:
    self.__enable_rebalancing = enable_rebalancing
    # ...
```

---

### **Testing Strategy**

Add tests that verify improvement:

```python
def test_rebalancing_improves_skill_balance():
    """Test that rebalancing reduces skill variance."""
    # Measure skill variance before and after
    # Assert variance_after ≤ variance_before

def test_rebalancing_deterministic():
    """Test same seed produces same rebalanced result."""
    # Run twice with same seed
    # Assert identical final teams
```

---

### **Recommendations Summary**

**Phase 1: Simple Greedy Rebalancing**
1. Keep snake draft as-is
2. After draft, calculate balance score
3. Find best same-role swap that improves score
4. Apply swap and repeat
5. Stop when no improvement for 10 consecutive rounds
6. Use adaptive weight normalization (no hard-coded thresholds)

**Phase 2: Enhanced (if needed)**
- Add cross-role swaps
- Try multiple random starting points (different seeds)
- Pick best result

**Benefits:**
- ✅ No hard-coded thresholds
- ✅ Deterministic with seed
- ✅ Flexible (adapts to any skill distribution)
- ✅ Preserves existing snake draft
- ✅ Simple to implement and test

**Key Design Principles:**
- No hard-coded numeric thresholds like MAX_SKILL_VARIANCE = 50
- All metrics normalized relative to actual player distribution
- Deterministic results with same seed
- Maximum flexibility and adaptability