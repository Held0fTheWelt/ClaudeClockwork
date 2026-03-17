```markdown
# Ollama Skill

## Description
Interacts with the Ollama language model via HTTP API to generate text based on prompts.

## Inputs
- `prompt` (string): The input prompt for generating text.
- `model` (string, optional): Name of the Ollama model to use.
- `temperature` (float, optional): Controls randomness in response generation (0.0 to 2.0).
- `top_p` (float, optional): Alternative way to control randomness, prioritizes top n tokens (0.0 to 1.0).
- `stream` (bool, optional): Whether to stream the response.

## Outputs
- `response` (string or array of strings): Generated text from Ollama. If streaming is enabled, returns an array of streamed responses.

## Task Types
- Text Generation

## Example Usage
```json
{
  "prompt": "Explain quantum computing in simple terms.",
  "model": "llama2",
  "temperature": 0.7,
  "top_p": 0.9,
  "stream": false
}
```

## Error Handling
- `InvalidModelError`: Occurs when the specified model is not available.
- `ConnectionError`: Raised if unable to connect to the Ollama server.
```
