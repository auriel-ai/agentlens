# AgentLens

[![Status: Pre-release](https://img.shields.io/badge/Status-Pre--release-yellow)](https://github.com/auriel-ai/agentlens)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

AgentLens is an open-source debugging toolkit for AI agents that enables offline recording, replay, failure analysis, and cost tracking. Built for developers who need efficient, local-first debugging without consuming API credits.

## Overview

When developing AI agents, debugging is costly and time-consuming. Each iteration requires API calls, resources, and careful tracking of what happened. AgentLens provides:

- **Offline debugging** - Record and replay agent runs without making additional API calls
- **Failure analysis** - Identify common failure patterns automatically
- **Cost tracking** - Monitor token usage and estimated API costs
- **Local-first workflow** - Everything runs on your machine with no external dependencies

## Installation

```bash
pip install agentlens
```

## Quick Start

```python
from agentlens import AgentLens

# Initialize AgentLens
lens = AgentLens()

# 1. Record agent runs with a decorator
@lens.record
def my_agent_function(query):
    # Your agent implementation
    return result

# Use your agent normally - AgentLens records in the background
response = my_agent_function("Process this data")

# 2. Or use the context manager for more control
with lens.context_record(model="gpt-4") as recording:
    # Your agent code here
    result = some_function()
    recording.log_run(
        input_data=query,
        output_data=result,
        token_usage={"prompt_tokens": 10, "completion_tokens": 20}
    )

# 3. Replay the last recorded run
lens.replay()

# 4. Analyze failures in the last run
lens.analyze()

# 5. Track estimated costs
lens.costs(all_runs=True)
```

## Framework Integrations

### LangChain Integration

```python
from agentlens import AgentLens
from agentlens.integrations.langchain import LangChainLens

# Initialize AgentLens and LangChainLens
lens = AgentLens()
lc_lens = LangChainLens(lens=lens)

# Wrap a LangChain LLM, Chain or Agent
llm = OpenAI(temperature=0.7)
wrapped_llm = lc_lens.wrap_llm(llm)

# Use wrapped components as normal
response = wrapped_llm("What are three best practices for writing clean code?")

# Wrap a LangChain Chain
chain = LLMChain(llm=llm, prompt=prompt)
wrapped_chain = lc_lens.wrap_chain(chain)

# Wrap a LangChain Agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
wrapped_agent = lc_lens.wrap_agent(agent)
```

### OpenAI Integration

```python
from agentlens import AgentLens
from agentlens.integrations.openai import OpenAILens
import openai

# Initialize AgentLens and OpenAILens
lens = AgentLens()
openai_lens = OpenAILens(lens=lens)

# Wrap the OpenAI client
client = openai.OpenAI()
wrapped_client = openai_lens.wrap_client(client)

# Use the wrapped client as normal
response = wrapped_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain debugging in one paragraph."}
    ]
)
```

## Key Features

### Run Recording

Records agent inputs, outputs, tool calls, and token usage to local storage without requiring additional API calls.

```python
@lens.record
def agent_function(input_query):
    # Agent implementation
    return result
```

Or using the context manager for more control:

```python
with lens.context_record(model="gpt-4") as recording:
    # Custom agent code
    result = process_query(query)
    recording.log_run(
        input_data=query,
        output_data=result,
        token_usage=token_count,
        tool_calls=tools_used
    )
```

### Offline Replay

Reproduces agent runs locally, allowing you to inspect each step without consuming API credits.

```python
# Replay the most recent run
lens.replay()

# Replay a specific run by ID
lens.replay(run_id=3)
```

### Failure Analysis

Automatically identifies common issues like timeouts, empty outputs, and potential hallucinations based on output patterns.

```python
# Analyze the most recent run
lens.analyze()

# Analyze a specific run
lens.analyze(run_id=3)
```

### Cost Tracking

Estimates API usage costs based on token counts and configurable pricing models.

```python
# Track costs for the most recent run
lens.costs()

# Track costs for all runs
lens.costs(all_runs=True)

# Track costs for a specific run
lens.costs(run_id=3)
```

## Command Line Interface

AgentLens includes a CLI for working with recorded runs:

```bash
# Replay a run
agentlens replay --file runs.jsonl

# Analyze a run
agentlens analyze --id 3 --file runs.jsonl

# Calculate costs
agentlens costs --all --file runs.jsonl
```

## Use Cases

- **Development iteration** - Debug agents locally without repeatedly hitting APIs
- **Cost optimization** - Identify expensive or inefficient patterns in agent behavior
- **Regression testing** - Verify agent behavior after code changes
- **Educational purposes** - Study and analyze agent decision patterns

## Framework Compatibility

Currently supporting:
- Direct Python function decorators and context managers
- LangChain (LLMs, Chains, and Agents)
- OpenAI Python client (both modern and legacy versions)
- Planning future support for CrewAI and other frameworks

## Comparison with Alternatives

AgentLens is focused specifically on offline debugging and development iteration, complementing production monitoring tools like LangSmith or Helicone.

| Feature | AgentLens | Production Monitors |
|---------|-----------|---------------------|
| Deployment | Local-only | Cloud/hosted |
| Focus | Development/debugging | Production monitoring |
| Cost | Free, open-source | Freemium/paid tiers |
| Integration | Single decorator | Platform-specific |
| Analysis | Offline-first | Real-time analytics |

## Development Setup

To set up AgentLens for development:

```bash
# Clone the repository
git clone https://github.com/auriel-ai/agentlens.git
cd agentlens

# Run the setup script
./setup_and_run.sh
```

## Examples

Check out the `examples/` directory for full examples including:
- Basic usage with the decorator and context manager
- LangChain integration examples
- OpenAI client integration
- Command line interface examples

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE)

