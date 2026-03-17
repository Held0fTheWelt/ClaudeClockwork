import os
from abc import ABC, abstractmethod

class SkillBase:
    pass  # Minimal base class as per requirements

class ClaudeCodeApply(SkillBase):
    def __init__(self):
        pass
        
    def run(self, **kwargs):
        file_path = kwargs.get('file_path')
        content = kwargs.get('content', '')
        create_if_missing = kwargs.get('create_if_missing', False)
        make_dirs = kwargs.get('make_dirs', True)

        # Safety check: Ensure path starts with allowed roots
        allowed_roots = {'.claude', 'claudeclockwork', 'tests', '.project'}
        
        # Normalize and validate file path
        normalized_path = os.path.normpath(file_path)
        if not normalized_path.startswith(allowed_roots):
            return {'status': 'error', 
                    'file_path': file_path,
                    'error': "Forbidden directory"}
            
        try:
            # Create parent directories if needed
            if make_dirs and create_if_missing:
                os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
                
            # Write content to file
            with open(normalized_path, 'w') as f:
                f.write(content)
                
            return {'status': 'ok', 
                    'file_path': normalized_path}
                    
        except Exception as e:
            return {'status': 'error',
                    'file_path': file_path,
                    'error': str(e)}
