f = open('backend/app/services/task_executor_service.py')
lines = f.readlines()
f.close()
while lines and lines[-1].strip() in ('```', ''):
    lines.pop()
with open('backend/app/services/task_executor_service.py', 'w') as f:
    f.writelines(lines)
print('✓ Fixed')
