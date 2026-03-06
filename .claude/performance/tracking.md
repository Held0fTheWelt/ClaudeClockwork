# Performance Tracking

## Purpose

Continuous measurement of system effectiveness — at agent level and system level.

---

## Per-Agent Metrics

| Metric | Description | Good | Bad |
|---|---|---|---|
| Task Completion Success | Completion without rework on 1st attempt | >80% | <60% |
| Error Rate | Errors per task (build errors, logic errors) | <2 | >5 |
| Rework Frequency | How often same task must be returned | 0–1 | >2 |
| Estimation Accuracy | Estimated vs. actual complexity | ±1 level | >±2 level |

---

## System-Level Metrics

| Metric | Description |
|---|---|
| Knowledge Growth | New patterns / references per 10 tasks |
| Documentation Coverage | % of implemented systems with current docs |
| Refactor Frequency | How often already completed tasks are revisited |
| Architecture Stability | Number of L5 escalations per month (less = better) |

---

## Log Format

Performance logs are saved according to `performance/log_template.md` in the project directory.
File naming scheme: `Docs/Reviews/PerfLog_YYYY-MM-DD_[TaskName].md`

---

## Aggregation

After every **10 completed major tasks**, Team Lead creates an aggregation report:

```markdown
## Performance Report: Tasks [N-M]
**Period:** YYYY-MM-DD to YYYY-MM-DD

### Success Rates
- Completion without rework: X%
- Average rework cycles: Y

### Escalation Analysis
- L0: N tasks
- L1: N tasks
- L2: N tasks  [Designer involved]
- L3+: N tasks [Critics involved]

### Most Frequent Problems
1. [Problem type] — occurred [N] times
2. [Problem type] — occurred [N] times

### Improvement Recommendation
[Concrete measure with rationale]
```

---

## Escalation on Performance Degradation

If within 10 tasks:
- Rework Frequency > 3 on average → Team Lead reviews Task Brief quality
- Estimation Accuracy > ±2 levels → revise complexity classification
- L3+ escalations > 30% of all tasks → request Systemic Critic review
