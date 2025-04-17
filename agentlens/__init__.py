__version__ = "0.1.0"

from .core import AgentLens, cli

# Import integrations if available, but don't fail if dependencies are missing
try:
    from .integrations.langchain import LangChainLens
except ImportError:
    pass

try:
    from .integrations.openai import OpenAILens
except ImportError:
    pass

__all__ = ["AgentLens", "cli"]