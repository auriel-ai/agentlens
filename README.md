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

## Usage

### Recording Agent Runs

```python
from agentlens import AgentLens

lens = AgentLens()

@lens.record
def agent_function(input_query):
    # Your agent implementation
    return result

# Use your agent normally - AgentLens records in the background
response = agent_function("Process this data")
```

### Replaying and Analyzing

```python
# Replay the last recorded run
lens.replay()

# Replay a specific run
lens.replay(run_id=3)

# Analyze failures in the last run
lens.analyze()

# Track estimated costs
lens.costs()
```

## Key Features

### Run Recording
Records agent inputs, outputs, tool calls, and token usage to local storage without requiring additional API calls.

### Offline Replay
Reproduces agent runs locally, allowing you to inspect each step without consuming API credits.

### Failure Analysis
Automatically identifies common issues like timeouts, empty outputs, and potential hallucinations based on output patterns.

### Cost Tracking
Estimates API usage costs based on token counts and configurable pricing models.

## Use Cases

- **Development iteration** - Debug agents locally without repeatedly hitting APIs
- **Cost optimization** - Identify expensive or inefficient patterns in agent behavior
- **Regression testing** - Verify agent behavior after code changes
- **Educational purposes** - Study and analyze agent decision patterns

## Framework Compatibility

Currently focusing on integration with:
- LangChain (primary)
- Planned support for CrewAI and other frameworks

## Comparison with Alternatives

AgentLens is focused specifically on offline debugging and development iteration, complementing production monitoring tools like LangSmith or Helicone.

| Feature | AgentLens | Production Monitors |
|---------|-----------|---------------------|
| Deployment | Local-only | Cloud/hosted |
| Focus | Development/debugging | Production monitoring |
| Cost | Free, open-source | Freemium/paid tiers |
| Integration | Single decorator | Platform-specific |
| Analysis | Offline-first | Real-time analytics |

## Roadmap

1. Core recording and replay functionality
2. Failure analysis capabilities
3. Cost tracking implementation
4. Framework integrations expansion
5. CLI tools for log management

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE)

