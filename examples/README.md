# llmtest Examples

This directory contains working examples demonstrating different providers.

## Examples

### 1. simple_test (Mock Provider)
**No API key required** - Great for learning and testing

```bash
cd simple_test
python run_test.py
```

Demonstrates:
- Mock provider with deterministic responses
- All 4 test types (grounding, injection, safety, regression concepts)
- Console and JSON reporting

### 2. openai_example (OpenAI Provider)
**Requires OPENAI_API_KEY**

```bash
export OPENAI_API_KEY=your-api-key-here
cd openai_example
python run_test.py
```

Demonstrates:
- OpenAI GPT-4o-mini integration
- Knowledge base / context injection
- Real LLM testing with grounding checks

### 3. anthropic_example (Anthropic Provider)
**Requires ANTHROPIC_API_KEY**

```bash
export ANTHROPIC_API_KEY=your-api-key-here
cd anthropic_example
python run_test.py
```

Demonstrates:
- Anthropic Claude 3 Haiku integration
- Knowledge base / context injection
- Real LLM testing with grounding checks

## Test Configuration

All examples include:
- `llmtest.yaml` - Test configuration
- `run_test.py` - Runnable Python script
- `docs/` - Knowledge base documents (where applicable)

## Installation

```bash
# For OpenAI examples
pip install llmtest[openai]

# For Anthropic examples
pip install llmtest[anthropic]

# For all providers
pip install llmtest[all]
```
