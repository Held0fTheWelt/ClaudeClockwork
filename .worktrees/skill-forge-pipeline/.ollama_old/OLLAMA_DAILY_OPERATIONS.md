# Ollama Daily Operations Guide

**Audience**: Operations Team, SRE, DevOps
**Date**: March 16, 2026
**Status**: Production-Ready

---

## Overview

This guide covers day-to-day operational procedures for maintaining stable Ollama service with single-model mode configuration.

---

## Daily Checklist

### Morning (Start of Shift)

**Time: 08:00 AM** (or start of your business day)

**Tasks** (5-10 minutes):

```
☐ Check service status
  Command: systemctl status ollama
  Expected: active (running) since [time]
  Action if failed: systemctl start ollama

☐ Verify API responsiveness
  Command: curl -I http://localhost:11434/api/tags
  Expected: HTTP/1.1 200 OK
  Latency: < 200ms
  Action if slow: Check system load

☐ Check memory usage
  Command: tasklist | grep ollama
  Expected: ~200MB (if no model loaded) or ~41GB (if model loaded)
  Alert if: > 40GB
  Action: See Emergency Recovery section

☐ Review overnight logs
  Command: tail -n 30 /var/log/ollama_daily_restart.log
  Expected: "Restart successful" from 02:00 AM
  Action if missing: Check if cron job ran

☐ Check for errors
  Command: journalctl -u ollama -n 20 --no-pager
  Expected: No ERROR or FATAL entries
  Action if found: Investigate the error

☐ Document any anomalies
  File: /var/log/ollama_operations.log
  Example: "2026-03-17 08:15 - Memory drifted to 38GB, monitoring"
```

### Hourly (During Business Hours)

**Time: Every 4 hours** (suggested: 12 PM, 4 PM, 8 PM)

**Quick Check** (2-3 minutes):

```bash
# One-liner health check
echo "=== Memory ===" && \
tasklist | grep ollama && \
echo "=== API ===" && \
curl -s http://localhost:11434/api/tags | jq '.models | length' && \
echo "models available"
```

**Expected Output**:
```
=== Memory ===
ollama.exe               12,345 MB  (or ~41,000 MB if model loaded)
=== API ===
60
models available
```

### Evening (End of Shift)

**Time: 17:00 PM** (or end of your business day)

**Tasks** (5 minutes):

```
☐ Check if any long-running tasks
  Command: curl -s http://localhost:11434/api/ps
  Expected: Empty or quick responses
  Action if long-running: Note it, will auto-finish or timeout

☐ Verify no stuck processes
  Command: ps aux | grep -i ollama | grep -v grep
  Expected: 2-3 processes (app, server, maybe 1 worker)
  Action if many: May indicate stuck tasks

☐ Document end-of-day metrics
  Example: "17:00 - Memory: 41GB, API: responsive, 0 errors"
  File: /var/log/ollama_operations.log

☐ No manual intervention needed before overnight restart
  (Automatic restart happens at 02:00 AM)

☐ Alert ops team if any issues found
  Send: Slack, email, or incident tracker
```

### Nightly (Automatic)

**Time: 02:00 AM UTC** (configurable)

**Automated Process**:

```bash
/etc/cron.daily/ollama_restart
```

**What Happens**:
1. Ollama service stops gracefully (SIGTERM)
2. Any remaining processes killed (SIGKILL)
3. Service restarts automatically
4. Verification check runs
5. Log entry recorded

**Expected Log Entry**:
```
[2026-03-17 02:00:15] Starting daily Ollama restart
[2026-03-17 02:00:25] Restart successful
```

**Action if Failed**:
- Automatic alert sent if verification fails
- Manual restart may be needed (see Emergency Recovery)

---

## Health Check Commands

### Quick Status (30 seconds)

```bash
#!/bin/bash
echo "=== Ollama Status ==="
systemctl status ollama --no-pager | grep -E "(Active|Restart)"

echo ""
echo "=== Memory Usage ==="
tasklist | grep -i ollama

echo ""
echo "=== API Health ==="
curl -m 5 -s http://localhost:11434/api/tags | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Models: {len(d.get(\"models\", []))}')" || echo "API: UNREACHABLE"

echo ""
echo "=== Running Models ==="
curl -s http://localhost:11434/api/ps | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Running: {len(d.get(\"models\", []))}') if 'models' in d else print('No models')" || echo "Unable to check"
```

### Detailed Diagnostics (2 minutes)

```bash
#!/bin/bash
echo "=== Detailed Ollama Diagnostics ==="
echo ""
echo "Process List:"
ps aux | grep -i ollama | grep -v grep

echo ""
echo "Memory/CPU Top 5:"
ps aux | head -1
ps aux | grep -i ollama | head -5

echo ""
echo "Network Connections:"
netstat -tuln | grep 11434 || echo "Port 11434 not listening"

echo ""
echo "Disk Usage (Ollama models):"
du -sh ~/.ollama/models 2>/dev/null || echo "Models dir: [check path]"

echo ""
echo "System Free Memory:"
free -h | grep "^Mem"

echo ""
echo "Last 20 Log Lines:"
tail -n 20 /var/log/ollama_daily_restart.log
```

### Performance Baseline (5 minutes)

```bash
#!/bin/bash
# Run this weekly to establish baseline metrics

echo "=== Performance Baseline Test ==="
echo "Time: $(date)"
echo ""

# Test 1: API responsiveness
echo "Test 1: /api/tags latency"
time curl -s http://localhost:11434/api/tags > /dev/null

# Test 2: Model list
echo ""
echo "Test 2: Available models"
curl -s http://localhost:11434/api/tags | jq '.models | length'

# Test 3: Running models
echo ""
echo "Test 3: Currently running models"
curl -s http://localhost:11434/api/ps | jq '.models | length' || echo "0"

echo ""
echo "Test 4: System load"
uptime

echo ""
echo "Test 5: Memory snapshot"
tasklist | grep ollama
```

---

## Common Issues and Quick Fixes

### Issue 1: API Returns 503 Service Unavailable

**Symptoms**:
```
curl: (7) Failed to connect to localhost port 11434: Connection refused
```

**Causes**:
1. Ollama service crashed
2. Ollama not started
3. Port 11434 blocked

**Quick Fix**:
```bash
# Step 1: Check if running
systemctl status ollama

# Step 2: If not running, start it
systemctl start ollama

# Step 3: Wait 3 seconds
sleep 3

# Step 4: Verify
curl http://localhost:11434/api/tags
```

**If Still Not Working**:
1. Check logs: `journalctl -u ollama -n 30`
2. Manual start: `ollama serve` (to see actual errors)
3. Restart system if stuck

### Issue 2: Memory Usage Growing (> 35GB)

**Symptoms**:
```
tasklist | grep ollama
> ollama.exe               36,000 MB
```

**Causes**:
1. Long-running task consuming memory
2. Memory leak in Ollama (rare)
3. Multiple models loaded (should not happen in single-model mode)

**Quick Fix**:
```bash
# Option 1: Wait for task to complete
# (If inference was slow, it may finish)

# Option 2: Check what's running
curl http://localhost:11434/api/ps | jq

# Option 3: If stuck, restart
systemctl restart ollama

# Option 4: If recurring, escalate to infrastructure team
```

### Issue 3: Timeout Errors in Logs

**Symptoms**:
```
ERROR: Request timed out after 180 seconds
```

**Causes**:
1. Heavy task taking too long
2. System under memory pressure (paging to disk)
3. GPU driver issue

**Quick Fix**:
```bash
# Step 1: Check memory
tasklist | grep ollama

# Step 2: If memory high (> 40GB), restart
systemctl restart ollama

# Step 3: Check GPU status (if applicable)
nvidia-smi

# Step 4: Retry request
curl -m 180 http://localhost:11434/api/generate \
  -d '{"model": "qwen2.5-72b:docs", "prompt": "Hello"}'
```

### Issue 4: Models Not Available

**Symptoms**:
```
curl http://localhost:11434/api/tags
> {"models":[]}  (empty list)
```

**Causes**:
1. Models directory corrupted
2. File permissions issue
3. First startup after fresh install

**Quick Fix**:
```bash
# Step 1: Check if models directory exists
ls -la ~/.ollama/models/

# Step 2: Check permissions
stat ~/.ollama/models/ | grep "Access:"

# Step 3: Fix if needed
chmod 755 ~/.ollama/models/
chmod 644 ~/.ollama/models/manifests/*

# Step 4: Restart Ollama
systemctl restart ollama

# Step 5: Re-pull models if corrupted
ollama pull qwen2.5-72b:latest
```

### Issue 5: Process Hangs (High CPU but No Output)

**Symptoms**:
```
curl: (7) Failed to connect
AND
ps aux shows ollama.exe at 95% CPU
```

**Causes**:
1. Ollama in infinite loop
2. GPU driver deadlock
3. Corrupted model

**Quick Fix**:
```bash
# Step 1: Forcefully kill process
pkill -9 ollama

# Step 2: Wait 3 seconds
sleep 3

# Step 3: Restart
systemctl start ollama

# Step 4: If happens again, check logs
journalctl -u ollama -n 100 --no-pager
```

---

## Performance Tuning

### Optimizing for Latency

**Goal**: Reduce time from request to first token

**Configuration**:
```bash
OLLAMA_KEEP_ALIVE=5m    # Keep model loaded longer (less reload time)
OLLAMA_NUM_PARALLEL=1   # Ensure no contention for GPU
OLLAMA_NUM_THREAD=16    # Match your CPU core count
```

**Check Current Settings**:
```bash
cat /etc/systemd/system/ollama.service | grep -i ollama
```

### Optimizing for Throughput

**Goal**: Process more requests per hour

**Strategy**:
1. Keep model warm (adjust OLLAMA_KEEP_ALIVE)
2. Minimize queue wait time
3. Use task batching where possible

**Monitor Queue**:
```bash
# Create a wrapper that counts pending requests
ps aux | grep "qwen2.5-72b" | grep -v grep | wc -l
```

### Optimizing for Stability

**Goal**: Never OOM or timeout

**Configuration**:
```bash
OLLAMA_KEEP_ALIVE=5m    # Unload after 5 min (default is safe)
OLLAMA_MAX_LOADED_MODELS=1  # Hard limit
OLLAMA_NUM_PARALLEL=1       # Serialized only
```

**Monitor Stability**:
```bash
# Log memory every minute
while true; do
  echo "[$(date)] $(tasklist | grep ollama | awk '{print $NF}')" >> /var/log/ollama_memory.log
  sleep 60
done
```

---

## Monitoring Dashboard (For Your Team)

### Suggested Metrics to Display

```
┌─────────────────────────────────────────┐
│        OLLAMA STATUS DASHBOARD          │
├─────────────────────────────────────────┤
│ Service Status: ✓ RUNNING               │
│ Memory Usage: 41.2 GB / 64 GB (64%)     │
│ API Latency: 48ms                       │
│ Models Available: 60                    │
│ Models Running: 1 (qwen2.5-72b)         │
│ Uptime: 23h 45m                         │
│ Next Restart: 2026-03-18 02:00 UTC      │
│ Error Rate: 0.0%                        │
│ Requests Last Hour: 15                  │
│ Avg Latency: 67 seconds                 │
└─────────────────────────────────────────┘
```

### Grafana Query Examples

**Memory Usage**:
```promql
# PromQL query if using Prometheus
process_resident_memory_bytes{job="ollama"} / 1e9
```

**Request Latency**:
```promql
histogram_quantile(0.95, rate(ollama_request_duration_seconds_bucket[5m]))
```

**Error Rate**:
```promql
rate(ollama_errors_total[5m])
```

---

## Alerting Rules

### Recommended Alert Thresholds

```yaml
# Prometheus alerting rules (example)

- alert: OllamaMemoryHigh
  expr: ollama_memory_usage_gb > 35
  for: 5m
  annotations:
    summary: "Ollama memory usage above 35GB"
    action: "Check running tasks, may auto-restart"

- alert: OllamaMemoryCritical
  expr: ollama_memory_usage_gb > 40
  for: 1m
  annotations:
    summary: "Ollama memory CRITICAL, auto-restarting"
    action: "Monitor restart process"

- alert: OllamaAPIDown
  expr: up{job="ollama"} == 0
  for: 2m
  annotations:
    summary: "Ollama API unreachable"
    action: "Manual restart required"

- alert: OllamaHighLatency
  expr: histogram_quantile(0.95, rate(ollama_latency[5m])) > 120
  for: 10m
  annotations:
    summary: "Ollama latency degraded"
    action: "Check system load and memory"
```

---

## Weekly Maintenance

### Every Monday (8 AM)

```
☐ Review logs from past week
  Command: grep ERROR /var/log/ollama*.log
  Expected: 0 entries
  Action if found: Investigate

☐ Check disk usage
  Command: du -sh ~/.ollama/models
  Expected: ~47 GB (qwen2.5-72b)
  Action if > 60GB: Investigate for extra models

☐ Test full recovery procedure
  Command: Follow "Emergency Recovery" section
  Expected: System recovers to healthy state

☐ Update monitoring dashboard
  Check if any metrics have drifted from baseline

☐ Team meeting
  Review: Incidents, performance, upcoming changes
```

### Every Friday (5 PM)

```
☐ Backup Ollama configuration
  Command: tar czf ollama_backup_$(date +%Y%m%d).tar.gz ~/.ollama/

☐ Verify backup can be restored
  Command: tar tzf ollama_backup_*.tar.gz | head -5

☐ Document any improvements made this week
  File: /var/log/ollama_improvements.log

☐ Plan for next week
  Are there any load increases expected?
  Any maintenance windows needed?
```

---

## Escalation Contact Tree

**Primary On-Call**:
- Name: [YOUR_OPS_ENGINEER]
- Phone: [PHONE]
- Email: [EMAIL]
- Available: [HOURS]

**Secondary**:
- Name: [YOUR_SECONDARY]
- Phone: [PHONE]
- Escalation: If primary unreachable > 15 minutes

**Infrastructure Lead**:
- Name: [YOUR_INFRA_LEAD]
- Escalation: For major incidents or system upgrade needs

**Vendor Support** (if applicable):
- Ollama: [SUPPORT_CONTACT]
- NVIDIA: [SUPPORT_CONTACT]
- For: GPU driver issues, Ollama bugs

---

## Communication Templates

### Incident Report Template

```
INCIDENT REPORT: Ollama [Issue Name]

Reported By: [YOUR_NAME]
Date/Time: [TIMESTAMP]
Duration: [START] - [END] ([MINUTES] minutes)

IMPACT:
- Services Affected: [LIST]
- Users Impacted: [COUNT/NAMES]
- Severity: Critical | High | Medium | Low

DESCRIPTION:
[What happened, exact symptoms observed]

ROOT CAUSE:
[What we think caused it]

RESOLUTION:
[What action was taken to fix it]

PREVENTION:
[What we'll do to prevent recurrence]

TIMELINE:
- HH:MM - Event noticed
- HH:MM - Diagnosis
- HH:MM - Resolution
- HH:MM - Verification

STAKEHOLDER UPDATES SENT:
- [ ] Slack #incident
- [ ] Email to team
- [ ] Status page
```

### End-of-Day Summary Template

```
OLLAMA OPERATIONS - Daily Summary
Date: [DATE]

METRICS:
- Uptime: [HH:MM] (should be 24h minus restart window)
- API Availability: 99.9%+
- Memory Peak: [XX] GB
- Tasks Processed: [COUNT]
- Errors: [COUNT]

INCIDENTS:
- [INCIDENT 1]: Description and resolution
- [INCIDENT 2]: Description and resolution
- None (if no issues)

OBSERVATIONS:
- [OBSERVATION 1]
- [OBSERVATION 2]

NOTES:
- Next scheduled maintenance: [DATE] at [TIME]
- Any items for team meeting: [YES/NO, LIST]

Reported By: [YOUR_NAME]
```

---

## Additional Resources

### Configuration Files
- Ollama Config: `~/.ollama/config.json`
- Setup Script: `.ollama/ollama_setup.py`
- Monitor Script: `.ollama/monitor_ollama_memory.py`

### Documentation
- Architecture: `.ollama/OLLAMA_ARCHITECTURE.md`
- Recovery: `.ollama/OLLAMA_EMERGENCY_RECOVERY.md`
- Final Report: `.ollama/PHASE_6_FINAL_REPORT.md`

### Useful Commands

```bash
# Status and health
systemctl status ollama
curl http://localhost:11434/api/tags
curl http://localhost:11434/api/ps

# Logs
journalctl -u ollama -f  # Follow real-time
journalctl -u ollama -n 100  # Last 100 lines
tail -f /var/log/ollama_daily_restart.log

# Process management
systemctl restart ollama
systemctl stop ollama
systemctl start ollama

# Memory
tasklist | grep ollama
free -h
df -h ~/.ollama

# Network
netstat -tuln | grep 11434
ss -ln | grep 11434
```

---

**Document Status**: Production-Ready
**Last Updated**: 2026-03-16 17:00 UTC
**Next Review**: 2026-04-16

