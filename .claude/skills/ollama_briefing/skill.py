import json
import requests
from claudeclockwork.localai.local_ollama_runtime import LocalOllamaRuntimeConfig
from claudeclockwork.core.base.skill_base import SkillBase
from claudeclockwork.core.models.execution_context import ExecutionContext
from claudeclockwork.core.models.skill_result import SkillResult


def parse_ollama_response(response) -> str:
    """Parse Ollama streaming JSON response."""
    try:
        lines = response.text.strip().split('\n')
        content = ""
        for line in lines:
            if line:
                data = json.loads(line)
                if "response" in data and data["response"].strip():
                    content += data["response"]
                if data.get("done", False):
                    break
        return content
    except json.JSONDecodeError as e:
        return f"JSON error: {e}"
    except Exception as e:
        return f"Error: {e}"


class OllamaBriefingSkill(SkillBase):
    def run(self, context: ExecutionContext, **kwargs) -> SkillResult:
        """Generate structured content using Ollama models."""
        try:
            prompt = kwargs.get('prompt', '')
            task_type = kwargs.get('task_type', 'brief')
            model = kwargs.get('model', LocalOllamaRuntimeConfig.get_default_model())
            base_url = kwargs.get('base_url', LocalOllamaRuntimeConfig.get_base_url())
            timeout_seconds = int(kwargs.get('timeout_seconds', LocalOllamaRuntimeConfig.get_timeout('request')))
            num_ctx = int(kwargs.get('num_ctx', 4096))
            num_predict = int(kwargs.get('num_predict', 512))
            temperature = float(kwargs.get('temperature', 0.7))
            write_output_path = kwargs.get('write_output_path', None)
            metadata = kwargs.get('metadata', {})

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
                return SkillResult(
                    skill_name='ollama_briefing',
                    success=False,
                    data={
                        'status': 'error',
                        'skill_id': 'ollama_briefing',
                        'message': f'API returned status code {response.status_code}'
                    },
                    error=f"API returned status code {response.status_code}"
                )

            content = parse_ollama_response(response)

            if not content or content.startswith("Error:") or content.startswith("JSON error:"):
                return SkillResult(
                    skill_name='ollama_briefing',
                    success=False,
                    data={
                        'status': 'error',
                        'skill_id': 'ollama_briefing',
                        'message': f"Failed to parse response: {content}"
                    },
                    error=f"Failed to parse response: {content}"
                )

            if write_output_path:
                with open(write_output_path, 'w') as f:
                    f.write(content)

            return SkillResult(
                skill_name='ollama_briefing',
                success=True,
                data={
                    'status': 'ok',
                    'skill_id': 'ollama_briefing',
                    'model': model,
                    'task_type': task_type,
                    'content': content,
                    'base_url': base_url,
                    'timeout_seconds': timeout_seconds,
                    'metadata': metadata
                }
            )

        except Exception as e:
            return SkillResult(
                skill_name='ollama_briefing',
                success=False,
                data={
                    'status': 'error',
                    'skill_id': 'ollama_briefing',
                    'message': f"Error: {str(e)}"
                },
                error=f"Error: {str(e)}"
            )
