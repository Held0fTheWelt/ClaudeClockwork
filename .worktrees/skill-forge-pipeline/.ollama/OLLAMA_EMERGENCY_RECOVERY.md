# Ollama Emergency Recovery Procedures

**Audience**: Operations Team, On-Call Engineers
**Date**: March 16, 2026
**Status**: Production-Ready
**Severity**: High - Use only during incidents

---

## Quick Reference Card

### When to Use This Guide

```
☐ Ollama service is down
☐ API is unresponsive (timeout / 503)
☐ Memory usage exceeds 40GB
☐ Process is hung (high CPU, no output)
☐ Models not loading or responding
☐ Cascading request failures (>10% error rate)
```

### Emergency Contact Tree

```
Level 1 (Immediate):   Your On-Call Engineer
Level 2 (5 min):       Infrastructure Team Lead
Level 3 (15 min):      System Administrator
Level 4 (30 min):      Vendor Support (NVIDIA, Ollama if applicable)
```

---

## Incident Severity Levels

### Level 1: CRITICAL (Restore in < 5 minutes)

**Symptoms**:
- API completely unresponsive
- All requests failing
- Error rate: 100%

**SLA**: 5-minute recovery

**Procedure**: Emergency Restart (see below)

### Level 2: DEGRADED (Restore in < 30 minutes)

**Symptoms**:
- API responding but slow (>120s latency)
- Some requests timing out
- Memory > 35GB
- Error rate: 20-50%

**SLA**: 30-minute recovery

**Procedure**: Memory Cleanup (see below)

### Level 3: WARNING (Monitoring)

**Symptoms**:
- Unusual memory growth
- Occasional timeouts
- Performance below baseline
- Error rate: 1-10%

**SLA**: 2-hour investigation

**Procedure**: Diagnostic Check (see below)

---

## Procedure 1: Emergency Restart (5 minutes)

**When to Use**: Service is completely down or unresponsive

**Steps**:

### Step 1: Verify Service Is Down (30 seconds)

```bash
# Check if responding
curl -m 3 http://localhost:11434/api/tags
# Expected if down: timeout or "Connection refused"

# Check service status
systemctl status ollama
# Expected if down: inactive (dead) or failed
```

### Step 2: Stop Service Gracefully (1 minute)

```bash
# Attempt graceful shutdown
systemctl stop ollama

# Wait for graceful termination
sleep 5

# Verify stopped
ps aux | grep -i ollama | grep -v grep
# Expected: empty (no processes)

# If still running, force kill
pkill -9 ollama || true
sleep 2
```

### Step 3: Clean Up Temporary Files (30 seconds)

```bash
# Clear temp files (optional but recommended)
rm -rf ~/.ollama/tmp/* 2>/dev/null || true
rm -rf /tmp/ollama* 2>/dev/null || true

# Clear any stale locks
rm -f ~/.ollama/.lock 2>/dev/null || true
```

### Step 4: Restart Service (1 minute)

```bash
# Start service
systemctl start ollama

# Wait for startup
sleep 3

# Verify status
systemctl status ollama --no-pager
# Expected: active (running)
```

### Step 5: Verify Functionality (1 minute)

```bash
# Test API responsiveness
curl -m 5 http://localhost:11434/api/tags
# Expected: HTTP 200 with model list

# Verify models loaded
curl http://localhost:11434/api/tags | jq '.models | length'
# Expected: 60+

# Check memory (should be low after fresh start)
tasklist | grep ollama
# Expected: ~200MB (no model loaded yet)
```

### Recovery Complete ✓

```
Incident: Ollama unresponsive
Time to Recover: [ELAPSED_TIME] minutes
Status: ✓ RESTORED
Next: Monitor for recurrence
```

---

## Procedure 2: Memory Cleanup (10 minutes)

**When to Use**: Memory > 35GB but service still running

**Symptoms**:
- tasklist shows ollama.exe > 35GB
- Performance degrading
- Occasional timeouts

**Steps**:

### Step 1: Identify Memory Consumer (1 minute)

```bash
# Check which process is using memory
tasklist /v /FO CSV | grep ollama

# Get PID of memory-heavy process
OLLAMA_PID=$(ps aux | grep "[o]llama" | awk '{print $2}' | head -1)
echo "Ollama PID: $OLLAMA_PID"

# Check what it's doing
cat /proc/$OLLAMA_PID/status 2>/dev/null | grep VmRSS
# Or on Windows: wmic process where handle=$OLLAMA_PID get workingsetsize
```

### Step 2: Check Running Tasks (1 minute)

```bash
# See what models are loaded
curl http://localhost:11434/api/ps

# See if any inference in progress
curl http://localhost:11434/api/ps | jq '.models[].name'
# If empty: No models running

# If model running, wait for completion
# (Most inferences complete in < 180 seconds)
```

### Step 3: Force Model Unload (2 minutes)

```bash
# Option A: If service is responsive, unload model
curl http://localhost:11434/api/generate \
  -d '{"model": "qwen2.5-72b:docs", "prompt": ""}' \
  -X POST -m 10

# Or more directly, restart the service gracefully
systemctl restart ollama --no-block

# Wait for graceful shutdown
sleep 10

# Verify unload
curl http://localhost:11434/api/ps
# Expected: {"models":[]}
```

### Step 4: Verify Memory Released (2 minutes)

```bash
# Check memory after unload/restart
tasklist | grep ollama
# Expected: ~200MB (base process only)

# If still high (>1GB), force kill and restart
pkill -9 ollama || true
sleep 2
systemctl start ollama
sleep 3

# Verify
tasklist | grep ollama
# Expected: ~200MB
```

### Step 5: Resume Service (2 minutes)

```bash
# Service should already be running after restart
systemctl status ollama

# Verify API is responsive
curl http://localhost:11434/api/tags

# Document incident
echo "[$(date)] Memory cleanup: Ollama restarted, memory released" >> /var/log/ollama_incidents.log
```

### Recovery Complete ✓

```
Incident: High memory usage
Time to Recover: [ELAPSED_TIME] minutes
Memory Before: [XX] GB
Memory After: 0.2 GB
Status: ✓ RESOLVED
Action: Enable memory monitoring
```

---

## Procedure 3: Stuck Process Recovery (15 minutes)

**When to Use**: Process hung (high CPU but no output/response)

**Symptoms**:
- API timeout on all requests
- ps aux shows ollama at 95%+ CPU
- Service won't respond to commands
- curl timeouts

**Steps**:

### Step 1: Confirm Process Is Stuck (1 minute)

```bash
# Check if responsive
curl -m 3 http://localhost:11434/api/tags
# Expected if stuck: timeout

# Check CPU usage
ps aux | grep -i ollama | grep -v grep
# Look for: CPU% > 80, TIME increasing

# Check if process is defunct or zombie
ps aux | grep -i ollama | grep Z
# If present: Process is truly stuck
```

### Step 2: Stop Service Immediately (1 minute)

```bash
# Attempt graceful stop (may not work if stuck)
systemctl stop ollama
sleep 3

# If systemctl doesn't work, force kill
pkill -9 ollama

# Verify all processes killed
ps aux | grep -i ollama | grep -v grep
# Expected: empty
```

### Step 3: Check System Resources (2 minutes)

```bash
# Check if system is in bad state
free -h        # Memory
df -h /        # Disk space
top -b -n 1 | head -20  # CPU load

# If disk full or memory critically low, address that first
# (See System Recovery section below)
```

### Step 4: Restart Service (2 minutes)

```bash
# Clear any stale state
rm -rf ~/.ollama/tmp/*
rm -f ~/.ollama/.lock

# Restart service
systemctl start ollama

# Wait for stability
sleep 5

# Verify health
curl http://localhost:11434/api/tags
# Expected: HTTP 200 with models
```

### Step 5: Investigate Root Cause (5 minutes)

```bash
# Check logs for errors
journalctl -u ollama -n 100 --no-pager

# Look for patterns:
# - GPU driver errors
# - Out of memory messages
# - Infinite loops

# If found, note in incident log:
echo "STUCK_PROCESS_INCIDENT: [DETAILS]" >> /var/log/ollama_incidents.log
```

### Recovery Complete ✓

```
Incident: Process hung
Time to Recover: [ELAPSED_TIME] minutes
Root Cause: [IDENTIFIED/UNKNOWN]
Status: ✓ RECOVERED
Action: Monitor closely, escalate if repeats
```

---

## Procedure 4: Out of Memory Recovery (10 minutes)

**When to Use**: Memory error, swap thrashing, or system unresponsive

**Symptoms**:
- Error: "Cannot allocate memory"
- System very slow (disk I/O at 100%)
- Swap usage > 10GB
- OOM killer messages in dmesg

**Steps**:

### Step 1: Verify OOM Condition (1 minute)

```bash
# Check swap usage
free -h | grep -i swap
# If > 5GB in use: System in distress

# Check dmesg for OOM killer
dmesg | tail -20 | grep -i "oom\|killed"

# Check available memory
free -h | grep "^Mem:"
# If free < 1GB: Critical
```

### Step 2: Kill Non-Essential Processes (2 minutes)

```bash
# List memory hogs
ps aux --sort=-%mem | head -10

# Kill user-facing apps (keep only Ollama + OS)
pkill -f slack 2>/dev/null || true
pkill -f chrome 2>/dev/null || true
pkill -f vscode 2>/dev/null || true

# Verify memory freed
free -h
```

### Step 3: Stop Ollama (1 minute)

```bash
# Stop gracefully
systemctl stop ollama
sleep 3

# Force kill if needed
pkill -9 ollama || true
```

### Step 4: Clear Caches (2 minutes)

```bash
# Drop filesystem caches (risky but effective)
sync  # Flush to disk
echo 3 > /proc/sys/vm/drop_caches

# Check freed memory
free -h
```

### Step 5: Restart Ollama (2 minutes)

```bash
# Start service
systemctl start ollama
sleep 5

# Verify
curl http://localhost:11434/api/tags
free -h
```

### Step 6: Escalate for Investigation (N/A)

```bash
# This indicates a serious resource issue
# Contact Infrastructure Team:
# "System hit OOM with only Ollama running"
# "Need to investigate: memory leak or insufficient RAM"

# Recommended: Reduce model size or upgrade RAM
```

### Recovery Complete ✓

```
Incident: Out of memory
Time to Recover: [ELAPSED_TIME] minutes
System Status: ✓ RECOVERED (may be unstable)
Action: ESCALATE - Infrastructure review needed
```

---

## Procedure 5: Port Conflict Recovery (5 minutes)

**When to Use**: "Address already in use" error on startup

**Symptoms**:
- systemctl start ollama fails
- Error: "Address already in use" or "bind: address in use"
- Port 11434 not listening

**Steps**:

### Step 1: Identify Process Using Port (1 minute)

```bash
# Find process on port 11434
lsof -i :11434
# Or:
netstat -tlnp | grep 11434

# Note the PID (if shown)
```

### Step 2: Stop Conflicting Process (2 minutes)

```bash
# If old Ollama process:
pkill -9 ollama
sleep 2

# If other service, stop it:
systemctl stop [service_name]

# Verify port is free
netstat -tlnp | grep 11434
# Expected: nothing

# Or check with curl
curl http://localhost:11434/api/tags
# Expected: Connection refused
```

### Step 3: Restart Ollama (1 minute)

```bash
# Start service
systemctl start ollama
sleep 3

# Verify
curl http://localhost:11434/api/tags
```

### Recovery Complete ✓

```
Incident: Port in use
Time to Recover: [ELAPSED_TIME] minutes
Conflicting Process: [IDENTIFIED]
Status: ✓ RESOLVED
```

---

## System-Level Recovery Procedures

### If Entire System Unresponsive

**Last Resort**: System Reboot

```bash
# Graceful shutdown
sync
systemctl poweroff

# Or emergency reboot
reboot -f

# After reboot:
# 1. Service should auto-start (if enabled)
# 2. Verify with: systemctl status ollama
# 3. Check API: curl http://localhost:11434/api/tags
```

### If GPU Driver Issues

**Symptoms**:
- CUDA errors in logs
- GPU at 100% but slow
- Ollama can't offload to GPU

**Recovery**:
```bash
# Check GPU
nvidia-smi

# If errors, restart GPU driver
sudo systemctl restart nvidia-persistenced

# Or reboot system
reboot
```

### If Disk Full

**Symptoms**:
- "No space left on device"
- df / shows 100%

**Recovery**:
```bash
# Check what's using space
du -sh ~/.ollama/models/*

# Clear old models if safe:
ollama rm old_model_name

# Or add disk space (infrastructure task)
```

---

## Post-Recovery Checklist

After any incident, complete this checklist:

```
☐ Service is running and responsive
  Command: systemctl status ollama
  Command: curl http://localhost:11434/api/tags

☐ Memory is at baseline
  Command: tasklist | grep ollama
  Expected: ~200MB or ~41GB (if model loaded)

☐ No errors in logs
  Command: journalctl -u ollama -n 50 | grep -i error
  Expected: empty (or only old errors)

☐ Document the incident
  File: /var/log/ollama_incidents.log
  Include: Time, symptoms, recovery procedure, root cause

☐ Notify stakeholders
  Slack: #incidents channel
  Email: On-call team lead

☐ Schedule post-mortem (if severity > LOW)
  When: Within 24 hours
  Duration: 30-60 minutes
  Purpose: Root cause analysis and prevention

☐ Monitor closely
  Next 2 hours: Check every 15 minutes
  Next 24 hours: Check hourly
```

---

## Escalation Decision Tree

```
Incident Occurs
│
├─ Service Down?
│  ├─ YES → Use Procedure 1 (Emergency Restart)
│  │        Time to recover: 5 minutes
│  │        If fails → Escalate to Infrastructure
│  │
│  └─ NO → Go to next check
│
├─ Memory > 40GB?
│  ├─ YES → Use Procedure 2 (Memory Cleanup)
│  │        Time to recover: 10 minutes
│  │        If memory returns: OK, monitor
│  │        If repeats: Escalate (possible leak)
│  │
│  └─ NO → Go to next check
│
├─ Process Hung (High CPU)?
│  ├─ YES → Use Procedure 3 (Stuck Process)
│  │        Time to recover: 15 minutes
│  │        If repeats: Escalate (bug in Ollama)
│  │
│  └─ NO → Go to next check
│
├─ API Responding but Slow?
│  ├─ YES → Monitor and document
│  │        If improves in 5 min: OK
│  │        If continues: Escalate (performance investigation)
│  │
│  └─ NO → Check system resources
│
└─ System Resources Critical (OOM, disk full)?
   ├─ YES → Use Procedure 4 (System Recovery)
   │        Contact Infrastructure immediately
   │        Schedule upgrade/cleanup
   │
   └─ Unknown → Enable debug logging and investigate
                Document findings for team
```

---

## Prevention Checklist

To prevent incidents from recurring:

```
After Each Incident:

☐ Was it preventable?
  - Yes: Implement preventive measure
  - No: Document and move on

☐ Add monitoring if not present
  - High CPU alert (> 80% for > 1 min)
  - High memory alert (> 35GB)
  - API timeout alert (> 120s latency)
  - Disk space alert (> 80% full)

☐ Update runbooks
  - Add this scenario to daily_operations.md
  - Add workaround if found
  - Document time to recovery

☐ Training
  - Teach team the recovery procedure
  - Practice with simulation (monthly)
  - Update on-call documentation

☐ Automate if possible
  - Add automated restart at memory threshold
  - Add automated cleanup job
  - Add health check monitoring
```

---

## Contact Information Template

**Update These Before Production**:

```
PRIMARY ON-CALL ENGINEER
Name: ________________________
Phone: ______________________
Email: ______________________
Available: ___________________

SECONDARY ON-CALL
Name: ________________________
Phone: ______________________
Escalation: After 15 minutes if primary unreachable

INFRASTRUCTURE TEAM LEAD
Name: ________________________
Phone: ______________________
Email: ______________________
Escalation: For critical system issues

EXTERNAL VENDORS
Ollama Support: https://github.com/ollama/ollama/issues
NVIDIA Support: [CONTACT_INFO]
System Vendor: [CONTACT_INFO]

INCIDENT CHANNELS
Slack Channel: #incidents
Email List: incidents@company.com
Status Page: [URL]
War Room: [ZOOM_LINK]
```

---

## Appendix: Quick Recovery Commands

**Copy and Paste Ready**:

```bash
# Emergency restart (2 minutes)
systemctl stop ollama && sleep 3 && systemctl start ollama && sleep 3 && curl http://localhost:11434/api/tags

# Memory cleanup (force restart)
pkill -9 ollama && sleep 2 && systemctl start ollama && sleep 3 && tasklist | grep ollama

# Check health
curl http://localhost:11434/api/tags && echo "API OK" || echo "API FAILED"

# Full diagnostics
echo "=== Service ===" && systemctl status ollama --no-pager && \
echo "=== Memory ===" && tasklist | grep ollama && \
echo "=== API ===" && curl -m 5 http://localhost:11434/api/tags | jq '.models | length' && \
echo "=== Logs ===" && journalctl -u ollama -n 10 --no-pager
```

---

**Document Status**: Production-Ready
**Last Updated**: 2026-03-16 17:00 UTC
**Critical**: Keep printed copy on desk during on-call shifts

