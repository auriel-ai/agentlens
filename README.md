# AgentLens

Offline AI agent debugging: record, replay, analyze failures, and track costs—all free and local.

[![Status: Pre-release](https://img.shields.io/badge/Status-Pre--release-yellow)](https://github.com/auriel-ai/agentlens)

## Overview

AgentLens provides a lightweight framework for debugging AI agents without consuming API credits. It enables you to:

- Record agent interactions for offline replay
- Analyze failure patterns
- Track costs and usage metrics
- Debug complex agent workflows locally

## Installation

```bash
pip install agentlens  # Coming soon
```

## Quickstart

```python
from agentlens import AgentLens

# Initialize the lens
lens = AgentLens()

# Decorate your agent function
@lens.record
def my_agent(prompt):
    # Your agent implementation
    return f"Response to {prompt}"

# Run your agent
response = my_agent("Hello, agent!")

# Replay recorded interactions for debugging
lens.replay()
```

## Why AgentLens?

- **Cost Efficiency**: Debug without burning API credits
- **Offline Analysis**: Review agent behavior without live connections
- **Failure Detection**: Identify and fix issues in agent workflows
- **Performance Tracking**: Monitor resource usage and response times

## Status

🚧 **Work in progress** — Stay tuned for v0.1.0! 🚧

## License

[MIT](LICENSE)

