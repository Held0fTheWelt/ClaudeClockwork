# Self-Improvement Cycle

## Purpose

After every major task, the system analyzes its own performance, identifies inefficiencies, and implements improvements in governance and patterns.

---

## Post-Task Cycle

### Step 1: Performance Analysis (Team Lead)

```
- Fill out performance log (performance/log_template.md)
- Compare metrics with previous tasks
- Identify anomalies (rework spikes, escalation errors)
```

### Step 2: Adversarial Review (Optional But Recommended)

```
- Was the escalation level classification correct?
- Did an agent exceed their responsibility boundaries?
- Were patterns duplicated instead of reused?
```

### Step 3: Identify Inefficiencies

```
Common sources:
- Unclear acceptance criteria → improve Task Brief
- Missing patterns in .claude/python/patterns.md → extract pattern
- Wrong escalation level classification → adjust Decision Policy
- Redundant docs → task Librarian Agent with merge
```

### Step 4: Implement Improvements

```
Autonomous (L0):
- Extend patterns.md
- Write performance log
- Small clarifications in governance docs

Requires Review (L1-L2):
- New agent responsibilities
- Changed review steps

Requires Critic (L4):
- Governance rule changes
- Adjust escalation thresholds
```

### Step 5: Update Documentation

```
- .claude/python/patterns.md: new patterns
- MEMORY.md: stable insights
- Docs/Documentation/: if implementation docs affected
- .claude/governance/: if process improvement
```

### Step 6: Adjust Agent Rules (If Necessary)

```
Only for proven structural problems:
- Clean up responsibility overlaps
- Adjust thresholds
- Propose new agent roles (→ L4 escalation!)
```

---

## Periodic Review (Every 10 Major Tasks)

```
1. Evaluate agent effectiveness (which agents perform best?)
2. Adjust responsibilities (eliminate overlaps)
3. Refine escalation thresholds (too often? too rarely?)
4. Clean knowledge archive (outdated entries)
5. Request Systemic Critic overall assessment
```

---

## Anti-Patterns (What to Avoid)

- **Governance Creep**: New rules without removing old rules
- **Agent Proliferation**: New agents for every specialized task
- **Review Theater**: Reviews that always deliver APPROVED (no adversarial value)
- **Knowledge Silos**: Insights only in agent memory, not in `.claude/`
