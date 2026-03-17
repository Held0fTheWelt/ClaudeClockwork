import requests
import json
import logging
from typing import Dict

def run(request: Dict) -> Dict:
    try:
        prompt = request.get('prompt', '')
        task_type = request.get('task_type', 'brief')
        model = request.get('model', 'qwen3:8b')
        base_url = request.get('base_url', 'http://127.0.0.1:11434')
        timeout_seconds = int(request.get('timeout_seconds', 300))
        num_ctx = int(request.get('num_ctx', 4096))
        num_predict = int(request.get('num_predict', 512))
        temperature = float(request.get('temperature', 0.7))
        write_output_path = request.get('write_output_path', None)
        metadata = request.get('metadata', {})

        headers = {'Content-Type': 'application/json'}
        payload = {
            'model': model,
            'prompt': prompt,
            'temperature': temperature,
            'num_ctx': num_ctx,
            'num_predict': num_predict
        }

        response = requests.post(
            f'{base_url}/api/generate',
            headers=headers,
            json=payload,
            timeout=timeout_seconds
        )

        if response.status_code != 200:
            raise ValueError(f"API returned status code {response.status_code}")

        result = response.json()
        content = result.get('response', '')

        if write_output_path:
            with open(write_output_path, 'w') as f:
                f.write(content)

        return {
            'status': 'ok',
            'skill_id': 'ollama_briefing',
            'request_id': request.get('request_id', ''),
            'model': model,
            'task_type': task_type,
            'content': content,
            'base_url': base_url,
            'timeout_seconds': timeout_seconds,
            'metadata': metadata
        }

    except requests.exceptions.Timeout:
        return {'status': 'error', 'skill_id': 'ollama_briefing', 'error': 'Request timeout'}
    except requests.exceptions.ConnectionError:
        return {'status': 'error', 'skill_id': 'ollama_briefing', 'error': 'Ollama unavailable'}
    except Exception as e:
        return {'status': 'error', 'skill_id': 'ollama_briefing', 'error': str(e)}
