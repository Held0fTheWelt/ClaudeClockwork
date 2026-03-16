#!/bin/bash

cd /tmp

python3 << 'EOF'
import json, urllib.request, time
from datetime import datetime

def test(name, method, endpoint, data=None):
    url = f'http://localhost:11434{endpoint}'
    start = time.time()
    try:
        if data:
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method=method)
            r = urllib.request.urlopen(req, timeout=180)
        else:
            r = urllib.request.urlopen(url, timeout=180)
        result = json.loads(r.read())
        lat = (time.time() - start) * 1000
        ts = datetime.now().strftime('%H:%M:%S')
        print(f'[{ts}] {name}: OK ({lat:.0f}ms)')
        return True
    except Exception as e:
        lat = (time.time() - start) * 1000
        ts = datetime.now().strftime('%H:%M:%S')
        print(f'[{ts}] {name}: FAIL - {str(e)[:40]} ({lat:.0f}ms)')
        return False

print('=' * 60)
print('PHASE 5 - OLLAMA STABILITY TEST')
print('=' * 60)

p = 0
f = 0

print('\nPASS 1/2')
print('-' * 60)
if test('Test 1: /api/tags', 'GET', '/api/tags'): p += 1
else: f += 1
if test('Test 2: qwen3:8b small model', 'POST', '/api/chat', {'model': 'qwen3:8b', 'messages': [{'role': 'user', 'content': 'Hello'}], 'stream': False}): p += 1
else: f += 1
if test('Test 3: qwen2.5-72b heavy model', 'POST', '/api/chat', {'model': 'qwen2.5-72b:docs', 'messages': [{'role': 'user', 'content': 'Hello'}], 'stream': False}): p += 1
else: f += 1
if test('Test 4: clockwork simulation', 'POST', '/api/chat', {'model': 'qwen2.5-72b:docs', 'messages': [{'role': 'user', 'content': 'Explain what git does'}], 'stream': False}): p += 1
else: f += 1

print('\nWaiting 5 seconds between passes...')
time.sleep(5)

print('\nPASS 2/2')
print('-' * 60)
if test('Test 1: /api/tags', 'GET', '/api/tags'): p += 1
else: f += 1
if test('Test 2: qwen3:8b small model', 'POST', '/api/chat', {'model': 'qwen3:8b', 'messages': [{'role': 'user', 'content': 'Hello'}], 'stream': False}): p += 1
else: f += 1
if test('Test 3: qwen2.5-72b heavy model', 'POST', '/api/chat', {'model': 'qwen2.5-72b:docs', 'messages': [{'role': 'user', 'content': 'Hello'}], 'stream': False}): p += 1
else: f += 1
if test('Test 4: clockwork simulation', 'POST', '/api/chat', {'model': 'qwen2.5-72b:docs', 'messages': [{'role': 'user', 'content': 'Explain what git does'}], 'stream': False}): p += 1
else: f += 1

print('\n' + '=' * 60)
print('SUMMARY')
print('=' * 60)
print(f'Tests passed: {p}/8')
print(f'Tests failed: {f}/8')
print('')
if f == 0:
    print('[OK] STABILITY ASSESSMENT: STABLE')
    print('  All tests passed, no 499/500 errors')
    print('  Proceed to Phase 6: Final report')
else:
    print(f'[FAIL] STABILITY ASSESSMENT: UNSTABLE')
    print(f'  {f} test(s) failed')
    print('  Investigate and remediate before Phase 6')
EOF
